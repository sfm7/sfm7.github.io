"""
Madrid Property Tracker - Apify Idealista Scanner
==================================================
Uses an Apify actor to scrape Idealista listings for Madrid,
detects new listings and price changes, and persists everything to Neon.

Environment variables required:
    APIFY_API_TOKEN       - Your Apify API token (from console.apify.com)
    DATABASE_URL          - Neon PostgreSQL connection string
                           (postgresql://user:pass@host/dbname?sslmode=requhire)

Optional:
    APIFY_ACTOR           - Apify actor ID (default: igolaizola/idealista-scraper)
    SEARCH_URL            - Idealista search URL to scrape
                           (default: https://www.idealista.com/venta-viviendas/madrid-madrid/)
    MAX_ITEMS             - Maximum listings to fetch (default: 200)

Slack notifications (optional):
    SLACK_WEBHOOK_URL     - Incoming webhook URL from your Slack app
    SLACK_NEW_THRESHOLD   - Min new listings to trigger a notification (default: 2)
    SLACK_DROP_THRESHOLD  - Min price drops to trigger a notification (default: 1)
    DASHBOARD_URL         - Your dashboard URL included in the message
                           (default: https://sfm7.github.io/madrid-tracker/dashboard/)
"""

import os
import time
import logging
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
DEFAULT_ACTOR = "memo23/idealista-scraper"
DEFAULT_SEARCH_URL = "https://www.idealista.com/venta-viviendas/madrid-madrid/"
DEFAULT_MAX_ITEMS = 200


# ── Apify Scraper ─────────────────────────────────────────────────────────────
def fetch_all_properties(api_token: str) -> list[dict]:
    """Run the Apify Idealista actor and return all scraped listings."""
    client = ApifyClient(api_token)
    actor_id = os.getenv("APIFY_ACTOR", DEFAULT_ACTOR)
    search_url = os.getenv("SEARCH_URL") or DEFAULT_SEARCH_URL
    max_items = int(os.getenv("MAX_ITEMS", str(DEFAULT_MAX_ITEMS)))

    run_input = {
        "startUrls": [{"url": search_url}],
        "maxItems": max_items,
    }

    log.info(f"Starting Apify actor '{actor_id}' for URL: {search_url}")
    log.info(f"Max items: {max_items}")

    run = client.actor(actor_id).call(run_input=run_input)
    log.info(f"Actor run finished (status: {run.get('status')})")

    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)

    log.info(f"Retrieved {len(items)} listings from Apify")
    return items


# ── Normalize Apify output to our schema ──────────────────────────────────────
def normalize_property(raw: dict) -> dict:
    """
    Map memo23/idealista-scraper output to our internal property schema.
    The actor returns nested objects: basicInfo, ubication, moreCharacteristics, etc.
    """
    basic = raw.get("basicInfo", {}) or {}
    location = raw.get("ubication", {}) or {}
    chars = raw.get("moreCharacteristics", {}) or {}
    contact = raw.get("contactInfo", {}) or {}
    comments = raw.get("comments", []) or []

    # Extract description from comments
    description = ""
    if comments and isinstance(comments, list):
        description = comments[0].get("propertyComment", "") if comments else ""
    elif isinstance(comments, str):
        description = comments

    # Clean URL (remove tracking params)
    detail_url = raw.get("detailWebLink", "")
    if detail_url and "?" in detail_url:
        detail_url = detail_url.split("?")[0]

    return {
        "propertyCode": str(raw.get("adid", basic.get("propertyCode", ""))),
        "thumbnail": basic.get("thumbnail"),
        "numPhotos": basic.get("numPhotos"),
        "floor": basic.get("floor"),
        "price": raw.get("price") or basic.get("price"),
        "currencySuffix": "€",
        "propertyType": raw.get("propertyType", "homes"),
        "operation": raw.get("operation", "sale"),
        "size": chars.get("constructedArea") or chars.get("usableArea"),
        "rooms": chars.get("roomNumber"),
        "bathrooms": chars.get("bathNumber"),
        "address": location.get("title"),
        "province": location.get("administrativeAreaLevel1"),
        "municipality": location.get("administrativeAreaLevel2"),
        "district": location.get("administrativeAreaLevel3"),
        "country": raw.get("country", "es"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "description": description,
        "hasVideo": raw.get("has360VHS", False),
        "status": chars.get("status"),
        "features": {
            "hasAirConditioning": chars.get("airConditioning", False),
            "hasBoxRoom": chars.get("boxroom", False),
            "hasSwimmingPool": chars.get("swimmingPool", False),
            "hasGarden": chars.get("garden", False),
        },
        "agencyName": contact.get("commercialName"),
        "url": detail_url,
    }


# ── Database helpers ───────────────────────────────────────────────────────────
def get_db_conn():
    """Return a psycopg2 connection to Neon."""
    url = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    return conn


def upsert_property(cur, prop: dict) -> tuple[bool, bool]:
    """
    Insert or update a property.
    Returns (is_new, price_changed).
    """
    code = str(prop.get("propertyCode", ""))
    price = prop.get("price")
    features = prop.get("features", {}) or {}

    # Check existing
    cur.execute("SELECT price, is_active FROM properties WHERE property_code = %s", (code,))
    existing = cur.fetchone()

    is_new = existing is None
    price_changed = (not is_new) and (existing["price"] != price)

    now = datetime.now(timezone.utc)

    if is_new:
        cur.execute(
            """
            INSERT INTO properties (
                property_code, thumbnail, num_photos, floor, price,
                currency_suffix, property_type, operation, size, rooms,
                bathrooms, address, province, municipality, district,
                country, latitude, longitude, description, has_video,
                status, has_air_conditioning, has_box_room, has_swimming_pool,
                has_garden, agency_name, url,
                first_seen_at, last_seen_at, is_active
            ) VALUES (
                %(code)s, %(thumbnail)s, %(num_photos)s, %(floor)s, %(price)s,
                %(currency)s, %(prop_type)s, %(operation)s, %(size)s, %(rooms)s,
                %(bathrooms)s, %(address)s, %(province)s, %(municipality)s, %(district)s,
                %(country)s, %(lat)s, %(lon)s, %(description)s, %(has_video)s,
                %(status)s, %(has_ac)s, %(has_box)s, %(has_pool)s,
                %(has_garden)s, %(agency)s, %(url)s,
                %(now)s, %(now)s, TRUE
            )
            """,
            {
                "code": code,
                "thumbnail": prop.get("thumbnail"),
                "num_photos": prop.get("numPhotos"),
                "floor": prop.get("floor"),
                "price": price,
                "currency": prop.get("currencySuffix", "€"),
                "prop_type": prop.get("propertyType"),
                "operation": prop.get("operation"),
                "size": prop.get("size"),
                "rooms": prop.get("rooms"),
                "bathrooms": prop.get("bathrooms"),
                "address": prop.get("address"),
                "province": prop.get("province"),
                "municipality": prop.get("municipality"),
                "district": prop.get("district"),
                "country": prop.get("country"),
                "lat": prop.get("latitude"),
                "lon": prop.get("longitude"),
                "description": prop.get("description"),
                "has_video": prop.get("hasVideo", False),
                "status": prop.get("status"),
                "has_ac": features.get("hasAirConditioning", False),
                "has_box": features.get("hasBoxRoom", False),
                "has_pool": features.get("hasSwimmingPool", False),
                "has_garden": features.get("hasGarden", False),
                "agency": prop.get("agencyName"),
                "url": prop.get("url"),
                "now": now,
            },
        )
    else:
        # Update mutable fields + last_seen_at + re-activate if was inactive
        cur.execute(
            """
            UPDATE properties SET
                thumbnail = %(thumbnail)s,
                num_photos = %(num_photos)s,
                price = %(price)s,
                size = %(size)s,
                rooms = %(rooms)s,
                bathrooms = %(bathrooms)s,
                address = %(address)s,
                district = %(district)s,
                description = %(description)s,
                has_video = %(has_video)s,
                status = %(status)s,
                has_air_conditioning = %(has_ac)s,
                has_box_room = %(has_box)s,
                has_swimming_pool = %(has_pool)s,
                has_garden = %(has_garden)s,
                agency_name = %(agency)s,
                url = %(url)s,
                last_seen_at = %(now)s,
                is_active = TRUE
            WHERE property_code = %(code)s
            """,
            {
                "code": code,
                "thumbnail": prop.get("thumbnail"),
                "num_photos": prop.get("numPhotos"),
                "price": price,
                "size": prop.get("size"),
                "rooms": prop.get("rooms"),
                "bathrooms": prop.get("bathrooms"),
                "address": prop.get("address"),
                "district": prop.get("district"),
                "description": prop.get("description"),
                "has_video": prop.get("hasVideo", False),
                "status": prop.get("status"),
                "has_ac": features.get("hasAirConditioning", False),
                "has_box": features.get("hasBoxRoom", False),
                "has_pool": features.get("hasSwimmingPool", False),
                "has_garden": features.get("hasGarden", False),
                "agency": prop.get("agencyName"),
                "url": prop.get("url"),
                "now": now,
            },
        )

    # Always record price history when inserting OR when price changed
    if is_new or price_changed:
        cur.execute(
            "INSERT INTO price_history (property_code, price, recorded_at) VALUES (%s, %s, %s)",
            (code, price, now),
        )

    return is_new, price_changed


# ── Slack notifications ────────────────────────────────────────────────────────
DASHBOARD_URL = os.getenv(
    "DASHBOARD_URL",
    "https://sfm7.github.io/madrid-tracker/dashboard/",
)


def _fmt_price(price) -> str:
    if price is None:
        return "—"
    return f"€{int(price):,}".replace(",", ".")


def _property_block(prop: dict) -> dict:
    """Build a Slack Block Kit section for one property."""
    price     = prop.get("price")
    size      = prop.get("size")
    rooms     = prop.get("rooms")
    baths     = prop.get("bathrooms")
    district  = prop.get("district") or prop.get("municipality") or ""
    address   = prop.get("address") or ""
    url       = prop.get("url") or "#"
    thumbnail = prop.get("thumbnail")

    price_sqm = f"  ·  €{int(price/size):,}/m²".replace(",", ".") if price and size else ""
    specs = "  ·  ".join(filter(None, [
        f"🛏 {rooms}" if rooms else None,
        f"🚿 {baths}" if baths else None,
        f"📐 {size}m²" if size else None,
    ]))

    text = (
        f"*{_fmt_price(price)}*{price_sqm}\n"
        f"📍 {address}{f'  ·  {district}' if district else ''}\n"
        f"{specs}\n"
        f"<{url}|View on Idealista →>"
    )

    block: dict = {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text},
    }
    if thumbnail:
        block["accessory"] = {
            "type": "image",
            "image_url": thumbnail,
            "alt_text": address or "property",
        }
    return block


def notify_slack(
    new_props: list[dict],
    price_drop_props: list[dict],
    total_found: int,
    duration: float,
) -> None:
    """
    Send a Slack notification via incoming webhook.

    Fires only when:
      - new_props count >= SLACK_NEW_THRESHOLD (default 2), OR
      - price_drop_props count >= SLACK_DROP_THRESHOLD (default 1)
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        log.debug("SLACK_WEBHOOK_URL not set — skipping notification")
        return

    new_threshold  = int(os.getenv("SLACK_NEW_THRESHOLD",  "2"))
    drop_threshold = int(os.getenv("SLACK_DROP_THRESHOLD", "1"))

    has_new   = len(new_props)  >= new_threshold
    has_drops = len(price_drop_props) >= drop_threshold

    if not has_new and not has_drops:
        log.info(
            f"Slack: {len(new_props)} new (threshold {new_threshold}), "
            f"{len(price_drop_props)} drops (threshold {drop_threshold}) — skipping"
        )
        return

    blocks = []

    # ── New listings section ──────────────────────────────────────────────
    if has_new:
        n = len(new_props)
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🏠 {n} new Madrid listing{'s' if n != 1 else ''} found",
                "emoji": True,
            },
        })
        blocks.append({"type": "divider"})

        show_props = new_props[:4]   # max 4 cards per message
        for prop in show_props:
            blocks.append(_property_block(prop))
            blocks.append({"type": "divider"})

        if n > len(show_props):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_… and *{n - len(show_props)} more*. Open the dashboard to see all._",
                },
            })

    # ── Price drops section ───────────────────────────────────────────────
    if has_drops:
        nd = len(price_drop_props)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📉 {nd} price drop{'s' if nd != 1 else ''}*",
            },
        })
        blocks.append({"type": "divider"})

        for prop in price_drop_props[:3]:   # max 3 drops
            old_price = prop.get("_old_price")
            new_price = prop.get("price")
            drop_pct  = (
                round((new_price - old_price) / old_price * 100, 1)
                if old_price and new_price else None
            )
            drop_line = (
                f"  ·  ~~{_fmt_price(old_price)}~~ → *{_fmt_price(new_price)}*"
                f"  `{drop_pct:+.1f}%`" if drop_pct else ""
            )
            block = _property_block(prop)
            # prepend drop info to text
            block["text"]["text"] = drop_line + "\n" + block["text"]["text"]
            blocks.append(block)
            blocks.append({"type": "divider"})

    # ── Footer ────────────────────────────────────────────────────────────
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": (
                    f"Scanned {total_found} listings in {duration}s  ·  "
                    f"<{DASHBOARD_URL}|Open dashboard →>"
                ),
            }
        ],
    })

    payload = {"blocks": blocks}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        log.info("Slack notification sent")
    except Exception as exc:
        log.warning(f"Slack notification failed: {exc}")


def mark_gone_properties(cur, seen_codes: set[str]) -> int:
    """Mark properties not seen in this scan as inactive."""
    if not seen_codes:
        return 0
    cur.execute(
        """
        UPDATE properties SET is_active = FALSE, last_seen_at = NOW()
        WHERE is_active = TRUE
          AND property_code != ALL(%s)
        """,
        (list(seen_codes),),
    )
    return cur.rowcount


# ── Static JSON export ─────────────────────────────────────────────────────────
import json
from decimal import Decimal
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard" / "data"


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def export_static_json() -> None:
    """Query the DB and write static JSON files for the GitHub Pages dashboard."""
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_db_conn()
    cur = conn.cursor()

    # ── properties.json ───────────────────────────────────────────────────
    cur.execute("""
        SELECT p.*, ph_first.price AS initial_price
        FROM properties p
        LEFT JOIN (
            SELECT DISTINCT ON (property_code) property_code, price
            FROM price_history ORDER BY property_code, recorded_at ASC
        ) ph_first ON ph_first.property_code = p.property_code
        WHERE p.is_active = TRUE
        ORDER BY p.first_seen_at DESC
    """)
    properties = cur.fetchall()

    # ── price history per property ────────────────────────────────────────
    cur.execute("""
        SELECT property_code, price, recorded_at
        FROM price_history
        ORDER BY property_code, recorded_at DESC
    """)
    history_rows = cur.fetchall()
    history_map: dict[str, list] = {}
    for row in history_rows:
        code = row["property_code"]
        history_map.setdefault(code, []).append({
            "price": row["price"],
            "recorded_at": row["recorded_at"],
        })

    # ── stats ─────────────────────────────────────────────────────────────
    cur.execute("""
        SELECT COUNT(*) AS active_total,
               COUNT(*) FILTER (WHERE viewed = FALSE) AS unviewed,
               COUNT(*) FILTER (WHERE saved = TRUE) AS saved,
               COUNT(*) FILTER (WHERE first_seen_at > NOW() - INTERVAL '48 hours') AS new_48h,
               ROUND(AVG(price)::numeric, 0) AS avg_price,
               ROUND(AVG(price_per_sqm)::numeric, 0) AS avg_price_sqm,
               ROUND(MIN(price)::numeric, 0) AS min_price,
               ROUND(MAX(price)::numeric, 0) AS max_price
        FROM properties WHERE is_active = TRUE
    """)
    kpis = cur.fetchone()

    cur.execute("""
        SELECT district, COUNT(*) AS count, ROUND(AVG(price)::numeric, 0) AS avg_price
        FROM properties WHERE is_active = TRUE AND district IS NOT NULL
        GROUP BY district ORDER BY count DESC
    """)
    by_district = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) AS drops FROM v_properties_with_drop
        WHERE price_change_pct < 0
    """)
    price_drops = cur.fetchone()["drops"]

    cur.execute("SELECT * FROM scan_logs ORDER BY scanned_at DESC LIMIT 1")
    last_scan = cur.fetchone()

    conn.close()

    # ── Write properties.json ─────────────────────────────────────────────
    props_out = []
    for p in properties:
        props_out.append({
            "property_code": p["property_code"],
            "address": p["address"],
            "district": p["district"],
            "municipality": p["municipality"],
            "province": p["province"],
            "price": p["price"],
            "price_per_sqm": p["price_per_sqm"],
            "rooms": p["rooms"],
            "bathrooms": p["bathrooms"],
            "size": p["size"],
            "floor": p["floor"],
            "thumbnail": p["thumbnail"],
            "url": p["url"],
            "description": p["description"],
            "agency_name": p["agency_name"],
            "latitude": p["latitude"],
            "longitude": p["longitude"],
            "has_air_conditioning": p["has_air_conditioning"],
            "has_swimming_pool": p["has_swimming_pool"],
            "has_garden": p["has_garden"],
            "has_box_room": p["has_box_room"],
            "has_video": p["has_video"],
            "status": p["status"],
            "num_photos": p["num_photos"],
            "is_active": p["is_active"],
            "first_seen_at": p["first_seen_at"],
            "last_seen_at": p["last_seen_at"],
            "initial_price": p["initial_price"],
            "saved": p["saved"],
            "viewed": p["viewed"],
            "notes": p["notes"],
            "price_history": history_map.get(p["property_code"], []),
        })

    (DASHBOARD_DIR / "properties.json").write_text(
        json.dumps(props_out, cls=DecimalEncoder, ensure_ascii=False), encoding="utf-8"
    )
    log.info(f"Exported {len(props_out)} properties to properties.json")

    # ── Write stats.json ──────────────────────────────────────────────────
    stats_out = {
        "kpis": dict(kpis) if kpis else {},
        "by_district": [dict(d) for d in by_district],
        "price_drops": price_drops,
        "last_scan": dict(last_scan) if last_scan else None,
    }
    (DASHBOARD_DIR / "stats.json").write_text(
        json.dumps(stats_out, cls=DecimalEncoder, ensure_ascii=False), encoding="utf-8"
    )
    log.info("Exported stats.json")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    start = time.time()
    log.info("=" * 60)
    log.info("Madrid Property Tracker - Apify Scanner starting")
    log.info("=" * 60)

    api_token = os.environ.get("APIFY_API_TOKEN")
    if not api_token:
        raise RuntimeError("APIFY_API_TOKEN must be set")

    scan_status = "success"
    error_msg: Optional[str] = None
    new_count = price_change_count = removed_count = total_found = 0
    new_props:        list[dict] = []   # full dicts of new listings (for Slack)
    price_drop_props: list[dict] = []   # full dicts of price-dropped listings

    try:
        raw_properties = fetch_all_properties(api_token)
        properties = [normalize_property(p) for p in raw_properties]
        total_found = len(properties)
        log.info(f"Total properties fetched: {total_found}")

        conn = get_db_conn()
        try:
            cur = conn.cursor()
            seen_codes: set[str] = set()

            for prop in properties:
                code = str(prop.get("propertyCode", ""))
                if not code:
                    continue
                seen_codes.add(code)

                # Capture old price before upsert (for drop tracking)
                cur.execute(
                    "SELECT price FROM properties WHERE property_code = %s", (code,)
                )
                row = cur.fetchone()
                old_price = row["price"] if row else None

                is_new, price_changed = upsert_property(cur, prop)

                if is_new:
                    new_count += 1
                    new_props.append(prop)
                    log.info(f"  [NEW] {code} - {prop.get('district')} - {prop.get('price')}€")
                elif price_changed and old_price and prop.get("price") < old_price:
                    price_change_count += 1
                    drop_prop = dict(prop)
                    drop_prop["_old_price"] = old_price
                    price_drop_props.append(drop_prop)
                    log.info(f"  [PRICE DROP] {code} {old_price}€ → {prop.get('price')}€")
                elif price_changed:
                    price_change_count += 1
                    log.info(f"  [PRICE CHANGE] {code} -> {prop.get('price')}€")

            removed_count = mark_gone_properties(cur, seen_codes)
            if removed_count:
                log.info(f"Marked {removed_count} properties as inactive (no longer listed)")

            conn.commit()
            log.info("Database committed successfully")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    except Exception as exc:
        scan_status = "error"
        error_msg = str(exc)
        log.exception("Scanner failed")

    duration = round(time.time() - start, 2)

    # Log scan result
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO scan_logs (total_found, new_properties, price_changes, removed_count,
                                   status, error_message, duration_secs)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (total_found, new_count, price_change_count, removed_count,
             scan_status, error_msg, duration),
        )
        conn.commit()
        conn.close()
    except Exception as log_exc:
        log.warning(f"Could not write scan log: {log_exc}")

    log.info(
        f"Scan complete in {duration}s | "
        f"total={total_found} new={new_count} price_changes={price_change_count} "
        f"removed={removed_count} status={scan_status}"
    )

    # Send Slack notification (only fires when thresholds are met)
    notify_slack(new_props, price_drop_props, total_found, duration)

    # Export static JSON for GitHub Pages dashboard
    if scan_status == "success":
        try:
            export_static_json()
        except Exception as exc:
            log.warning(f"Static JSON export failed: {exc}")

    if scan_status == "error":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
