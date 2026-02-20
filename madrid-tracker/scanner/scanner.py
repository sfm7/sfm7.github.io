"""
Madrid Property Tracker - Idealista Scanner
============================================
Authenticates with Idealista OAuth2, scans for Madrid properties,
detects new listings and price changes, and persists everything to Neon.

Environment variables required:
    IDEALISTA_API_KEY     - Your Idealista API key (client_id)
    IDEALISTA_SECRET      - Your Idealista API secret (client_secret)
    DATABASE_URL          - Neon PostgreSQL connection string
                           (postgresql://user:pass@host/dbname?sslmode=require)

Optional:
    SCAN_CENTER_LAT       - Search center latitude  (default: 40.4168 = Madrid)
    SCAN_CENTER_LON       - Search center longitude (default: -3.7038 = Madrid)
    SCAN_DISTANCE_KM      - Radius in km            (default: 15)
    MIN_PRICE             - Minimum price filter     (default: none)
    MAX_PRICE             - Maximum price filter     (default: none)
    MIN_ROOMS             - Minimum rooms            (default: none)
    MIN_SIZE              - Minimum size m2          (default: none)
    OPERATION             - sale | rent              (default: sale)
    PROPERTY_TYPE         - homes | offices | premises | garages | bedrooms | newDevelopments (default: homes)
"""

import os
import time
import base64
import logging
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone
from typing import Optional

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
IDEALISTA_TOKEN_URL = "https://api.idealista.com/oauth/token"
IDEALISTA_SEARCH_URL = "https://api.idealista.com/3.5/es/search"
MAX_PAGES = 20          # Idealista caps results; each page has up to 50 items
PAGE_SIZE = 50
RATE_LIMIT_SLEEP = 1.5  # seconds between API calls (be polite)


# ── Idealista OAuth2 ───────────────────────────────────────────────────────────
def get_access_token(api_key: str, secret: str) -> str:
    """Exchange client credentials for a Bearer token."""
    credentials = base64.b64encode(f"{api_key}:{secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    resp = requests.post(
        IDEALISTA_TOKEN_URL,
        headers=headers,
        data={"grant_type": "client_credentials", "scope": "read"},
        timeout=15,
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise ValueError(f"No access_token in response: {resp.json()}")
    log.info("Obtained Idealista access token")
    return token


# ── Idealista Search ───────────────────────────────────────────────────────────
def search_properties(token: str, page: int = 1) -> dict:
    """Search Madrid properties for a given page."""
    params = {
        "country": "es",
        "language": "es",
        "maxItems": PAGE_SIZE,
        "numPage": page,
        "operation": os.getenv("OPERATION", "sale"),
        "propertyType": os.getenv("PROPERTY_TYPE", "homes"),
        "center": f"{os.getenv('SCAN_CENTER_LAT', '40.4168')},{os.getenv('SCAN_CENTER_LON', '-3.7038')}",
        "distance": int(float(os.getenv("SCAN_DISTANCE_KM", "15")) * 1000),  # metres
        "sort": "publicationDate",
        "order": "desc",
    }
    # Optional filters
    if os.getenv("MIN_PRICE"):
        params["minPrice"] = os.getenv("MIN_PRICE")
    if os.getenv("MAX_PRICE"):
        params["maxPrice"] = os.getenv("MAX_PRICE")
    if os.getenv("MIN_ROOMS"):
        params["minRooms"] = os.getenv("MIN_ROOMS")
    if os.getenv("MIN_SIZE"):
        params["minSize"] = os.getenv("MIN_SIZE")

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(IDEALISTA_SEARCH_URL, headers=headers, params=params, timeout=20)
    resp.raise_for_status()
    return resp.json()


def fetch_all_properties(token: str) -> list[dict]:
    """Paginate through all Idealista results."""
    all_items = []
    page = 1
    while page <= MAX_PAGES:
        log.info(f"Fetching page {page}…")
        data = search_properties(token, page)
        items = data.get("elementList", [])
        all_items.extend(items)
        total = data.get("total", 0)
        log.info(f"  Got {len(items)} items (total so far: {len(all_items)} / {total})")
        if len(all_items) >= total or not items:
            break
        page += 1
        time.sleep(RATE_LIMIT_SLEEP)
    return all_items


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


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    start = time.time()
    log.info("=" * 60)
    log.info("Madrid Property Tracker - Scanner starting")
    log.info("=" * 60)

    api_key = os.environ.get("IDEALISTA_API_KEY")
    secret = os.environ.get("IDEALISTA_SECRET")
    if not api_key or not secret:
        raise RuntimeError("IDEALISTA_API_KEY and IDEALISTA_SECRET must be set")

    scan_status = "success"
    error_msg: Optional[str] = None
    new_count = price_change_count = removed_count = total_found = 0

    try:
        token = get_access_token(api_key, secret)
        properties = fetch_all_properties(token)
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
                is_new, price_changed = upsert_property(cur, prop)
                if is_new:
                    new_count += 1
                    log.info(f"  [NEW] {code} - {prop.get('district')} - {prop.get('price')}€")
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

    if scan_status == "error":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
