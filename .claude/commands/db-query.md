# db-query

Run a quick diagnostic query against the Neon PostgreSQL database.

Requires `DATABASE_URL` to be set in your environment or `madrid-tracker/api/.env`.

```bash
source madrid-tracker/api/.env 2>/dev/null || true
psql "$DATABASE_URL" -c "
SELECT
  (SELECT COUNT(*) FROM properties) AS total_properties,
  (SELECT COUNT(*) FROM properties WHERE status = 'active') AS active,
  (SELECT COUNT(*) FROM price_history) AS price_events,
  (SELECT MAX(started_at) FROM scan_logs) AS last_scan;
"
```

To check recent price drops:
```bash
psql "$DATABASE_URL" -c "SELECT * FROM v_properties_with_drop ORDER BY price_drop_pct DESC LIMIT 10;"
```
