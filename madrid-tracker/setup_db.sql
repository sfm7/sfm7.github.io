-- Madrid Property Tracker - Neon PostgreSQL Schema
-- Run this once against your Neon database to initialize the schema

-- ============================================================
-- PROPERTIES TABLE
-- Core record for each property found on Idealista
-- ============================================================
CREATE TABLE IF NOT EXISTS properties (
    id                   SERIAL PRIMARY KEY,
    property_code        VARCHAR(20) UNIQUE NOT NULL,
    thumbnail            TEXT,
    num_photos           INT,
    floor                VARCHAR(10),
    price                DECIMAL(12,2),
    currency_suffix      VARCHAR(5) DEFAULT '€',
    property_type        VARCHAR(50),
    operation            VARCHAR(20),
    size                 DECIMAL(8,2),
    rooms                INT,
    bathrooms            INT,
    address              TEXT,
    province             VARCHAR(100),
    municipality         VARCHAR(100),
    district             VARCHAR(100),
    country              VARCHAR(5),
    latitude             DECIMAL(10,6),
    longitude            DECIMAL(10,6),
    description          TEXT,
    has_video            BOOLEAN DEFAULT FALSE,
    status               VARCHAR(50),
    -- Features
    has_air_conditioning BOOLEAN DEFAULT FALSE,
    has_box_room         BOOLEAN DEFAULT FALSE,
    has_swimming_pool    BOOLEAN DEFAULT FALSE,
    has_garden           BOOLEAN DEFAULT FALSE,
    agency_name          VARCHAR(200),
    url                  TEXT,
    -- Tracking metadata
    first_seen_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at         TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active            BOOLEAN DEFAULT TRUE,
    -- User actions
    viewed               BOOLEAN DEFAULT FALSE,
    saved                BOOLEAN DEFAULT FALSE,
    notes                TEXT,
    -- Computed helper
    price_per_sqm        DECIMAL(10,2) GENERATED ALWAYS AS (
                             CASE WHEN size > 0 THEN price / size ELSE NULL END
                         ) STORED
);

-- ============================================================
-- PRICE HISTORY TABLE
-- Tracks every price change so you can spot drops
-- ============================================================
CREATE TABLE IF NOT EXISTS price_history (
    id            SERIAL PRIMARY KEY,
    property_code VARCHAR(20) NOT NULL REFERENCES properties(property_code) ON DELETE CASCADE,
    price         DECIMAL(12,2) NOT NULL,
    recorded_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================
-- SCAN LOGS TABLE
-- Audit trail for every scanner run
-- ============================================================
CREATE TABLE IF NOT EXISTS scan_logs (
    id              SERIAL PRIMARY KEY,
    scanned_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_found     INT DEFAULT 0,
    new_properties  INT DEFAULT 0,
    price_changes   INT DEFAULT 0,
    removed_count   INT DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'success',   -- success | error
    error_message   TEXT,
    duration_secs   DECIMAL(8,2)
);

-- ============================================================
-- INDEXES for fast dashboard queries
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_properties_district    ON properties(district);
CREATE INDEX IF NOT EXISTS idx_properties_price       ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_is_active   ON properties(is_active);
CREATE INDEX IF NOT EXISTS idx_properties_saved       ON properties(saved);
CREATE INDEX IF NOT EXISTS idx_properties_first_seen  ON properties(first_seen_at DESC);
CREATE INDEX IF NOT EXISTS idx_properties_last_seen   ON properties(last_seen_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_history_code     ON price_history(property_code, recorded_at DESC);

-- ============================================================
-- USEFUL VIEWS
-- ============================================================

-- Latest price per property (for the dashboard)
CREATE OR REPLACE VIEW v_latest_price AS
SELECT DISTINCT ON (property_code)
    property_code,
    price AS current_price,
    recorded_at
FROM price_history
ORDER BY property_code, recorded_at DESC;

-- Properties with price drop info
CREATE OR REPLACE VIEW v_properties_with_drop AS
SELECT
    p.*,
    ph_first.price AS initial_price,
    ROUND((p.price - ph_first.price) / ph_first.price * 100, 2) AS price_change_pct
FROM properties p
LEFT JOIN (
    SELECT DISTINCT ON (property_code)
        property_code, price
    FROM price_history
    ORDER BY property_code, recorded_at ASC
) ph_first ON ph_first.property_code = p.property_code
WHERE p.is_active = TRUE;
