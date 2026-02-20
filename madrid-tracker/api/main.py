"""
Madrid Property Tracker - FastAPI Backend
==========================================
REST API that serves property data from Neon to the dashboard frontend.

Endpoints:
    GET  /                              - Health check
    GET  /properties                    - List properties (with filters & pagination)
    GET  /properties/{code}             - Single property detail + price history
    PATCH /properties/{code}/viewed     - Toggle viewed flag
    PATCH /properties/{code}/saved      - Toggle saved flag
    PATCH /properties/{code}/notes      - Update personal notes
    GET  /stats                         - Dashboard KPI summary
    GET  /scan-logs                     - Recent scanner run history
    POST /scan/trigger                  - Trigger a manual scan (optional)

Deploy to Railway:
    railway up   (uses Procfile)
"""

import os
import subprocess
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import get_db

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Madrid Property Tracker API",
    description="Personal real-estate opportunity scanner for Madrid",
    version="1.0.0",
)

# Allow requests from GitHub Pages (and localhost for dev)
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://sfm7.github.io,http://localhost:3000,http://127.0.0.1:5500",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ──────────────────────────────────────────────────────────
class NotesPayload(BaseModel):
    notes: str


# ── Health ───────────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "madrid-property-tracker"}


# ── Properties ───────────────────────────────────────────────────────────────
@app.get("/properties", tags=["properties"])
def list_properties(
    district: Optional[str] = Query(None, description="Filter by district"),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_rooms: Optional[int] = Query(None),
    max_rooms: Optional[int] = Query(None),
    min_size: Optional[float] = Query(None),
    operation: Optional[str] = Query(None, description="sale | rent"),
    property_type: Optional[str] = Query(None),
    saved: Optional[bool] = Query(None, description="Filter saved properties"),
    viewed: Optional[bool] = Query(None, description="Filter viewed/unviewed"),
    is_active: bool = Query(True, description="Only active (currently listed) properties"),
    new_only: bool = Query(False, description="Only properties seen in the last 48 hours"),
    price_drop: bool = Query(False, description="Only properties with a price drop"),
    sort: str = Query("first_seen_at", description="Sort field"),
    order: str = Query("desc", description="asc | desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Return paginated property list with optional filters."""
    allowed_sort = {
        "first_seen_at", "last_seen_at", "price", "size", "rooms",
        "price_per_sqm", "district",
    }
    if sort not in allowed_sort:
        sort = "first_seen_at"
    order = "ASC" if order.lower() == "asc" else "DESC"

    conditions = ["p.is_active = %(is_active)s"]
    params: dict = {"is_active": is_active}

    if district:
        conditions.append("p.district ILIKE %(district)s")
        params["district"] = f"%{district}%"
    if min_price is not None:
        conditions.append("p.price >= %(min_price)s")
        params["min_price"] = min_price
    if max_price is not None:
        conditions.append("p.price <= %(max_price)s")
        params["max_price"] = max_price
    if min_rooms is not None:
        conditions.append("p.rooms >= %(min_rooms)s")
        params["min_rooms"] = min_rooms
    if max_rooms is not None:
        conditions.append("p.rooms <= %(max_rooms)s")
        params["max_rooms"] = max_rooms
    if min_size is not None:
        conditions.append("p.size >= %(min_size)s")
        params["min_size"] = min_size
    if operation:
        conditions.append("p.operation = %(operation)s")
        params["operation"] = operation
    if property_type:
        conditions.append("p.property_type = %(property_type)s")
        params["property_type"] = property_type
    if saved is not None:
        conditions.append("p.saved = %(saved)s")
        params["saved"] = saved
    if viewed is not None:
        conditions.append("p.viewed = %(viewed)s")
        params["viewed"] = viewed
    if new_only:
        conditions.append("p.first_seen_at >= NOW() - INTERVAL '48 hours'")
    if price_drop:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM price_history ph1
                JOIN price_history ph2 ON ph2.property_code = ph1.property_code
                WHERE ph1.property_code = p.property_code
                  AND ph1.price < ph2.price
                  AND ph1.recorded_at > ph2.recorded_at
            )
        """)

    where_clause = " AND ".join(conditions)
    offset = (page - 1) * page_size
    params.update({"limit": page_size, "offset": offset})

    query = f"""
        SELECT
            p.*,
            (
                SELECT price FROM price_history
                WHERE property_code = p.property_code
                ORDER BY recorded_at ASC LIMIT 1
            ) AS initial_price
        FROM properties p
        WHERE {where_clause}
        ORDER BY p.{sort} {order}
        LIMIT %(limit)s OFFSET %(offset)s
    """

    count_query = f"SELECT COUNT(*) AS total FROM properties p WHERE {where_clause}"

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(count_query, params)
        total = cur.fetchone()["total"]
        cur.execute(query, params)
        rows = cur.fetchall()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": -(-total // page_size),  # ceil division
        "data": [dict(r) for r in rows],
    }


@app.get("/properties/{code}", tags=["properties"])
def get_property(code: str):
    """Return a single property with its full price history."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM properties WHERE property_code = %s", (code,))
        prop = cur.fetchone()
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        cur.execute(
            "SELECT price, recorded_at FROM price_history "
            "WHERE property_code = %s ORDER BY recorded_at ASC",
            (code,),
        )
        history = cur.fetchall()

    return {"property": dict(prop), "price_history": [dict(h) for h in history]}


@app.patch("/properties/{code}/viewed", tags=["actions"])
def toggle_viewed(code: str):
    """Toggle the 'viewed' flag on a property."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE properties SET viewed = NOT viewed WHERE property_code = %s RETURNING viewed",
            (code,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Property not found")
    return {"property_code": code, "viewed": row["viewed"]}


@app.patch("/properties/{code}/saved", tags=["actions"])
def toggle_saved(code: str):
    """Toggle the 'saved' flag on a property."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE properties SET saved = NOT saved WHERE property_code = %s RETURNING saved",
            (code,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Property not found")
    return {"property_code": code, "saved": row["saved"]}


@app.patch("/properties/{code}/notes", tags=["actions"])
def update_notes(code: str, payload: NotesPayload):
    """Update personal notes on a property."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE properties SET notes = %s WHERE property_code = %s RETURNING property_code",
            (payload.notes, code),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Property not found")
    return {"property_code": code, "notes": payload.notes}


# ── Stats ─────────────────────────────────────────────────────────────────────
@app.get("/stats", tags=["dashboard"])
def get_stats():
    """Dashboard KPI summary."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE is_active)                                   AS active_total,
                COUNT(*) FILTER (WHERE is_active AND NOT viewed)                    AS unviewed,
                COUNT(*) FILTER (WHERE saved)                                       AS saved,
                COUNT(*) FILTER (WHERE first_seen_at >= NOW() - INTERVAL '48h')     AS new_48h,
                AVG(price) FILTER (WHERE is_active)                                 AS avg_price,
                AVG(price_per_sqm) FILTER (WHERE is_active)                         AS avg_price_sqm,
                MIN(price) FILTER (WHERE is_active)                                 AS min_price,
                MAX(price) FILTER (WHERE is_active)                                 AS max_price
            FROM properties
            """
        )
        kpis = dict(cur.fetchone())

        # Properties by district
        cur.execute(
            """
            SELECT district, COUNT(*) AS count, AVG(price) AS avg_price
            FROM properties WHERE is_active
            GROUP BY district ORDER BY count DESC LIMIT 15
            """
        )
        by_district = [dict(r) for r in cur.fetchall()]

        # Price drops (more than one price history entry, latest < earliest)
        cur.execute(
            """
            SELECT COUNT(DISTINCT p.property_code) AS price_drop_count
            FROM properties p
            WHERE p.is_active
              AND (
                  SELECT COUNT(*) FROM price_history WHERE property_code = p.property_code
              ) > 1
              AND (
                  SELECT price FROM price_history WHERE property_code = p.property_code
                  ORDER BY recorded_at DESC LIMIT 1
              ) < (
                  SELECT price FROM price_history WHERE property_code = p.property_code
                  ORDER BY recorded_at ASC LIMIT 1
              )
            """
        )
        price_drops = cur.fetchone()["price_drop_count"]

        # Last scan info
        cur.execute(
            "SELECT * FROM scan_logs ORDER BY scanned_at DESC LIMIT 1"
        )
        last_scan = cur.fetchone()

    return {
        "kpis": kpis,
        "by_district": by_district,
        "price_drops": price_drops,
        "last_scan": dict(last_scan) if last_scan else None,
    }


# ── Scan logs ─────────────────────────────────────────────────────────────────
@app.get("/scan-logs", tags=["dashboard"])
def get_scan_logs(limit: int = Query(20, ge=1, le=100)):
    """Recent scanner run history."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM scan_logs ORDER BY scanned_at DESC LIMIT %s", (limit,)
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


# ── Manual scan trigger ───────────────────────────────────────────────────────
@app.post("/scan/trigger", tags=["scanner"])
def trigger_scan():
    """
    Kick off a scanner run immediately.
    The scanner script must be accessible at ../scanner/scanner.py
    and environment variables must be set.
    """
    try:
        proc = subprocess.Popen(
            ["python", "../scanner/scanner.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return {"status": "started", "pid": proc.pid}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
