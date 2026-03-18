# CLAUDE.md — sfm7.github.io

## Project Overview

This repo contains two independent projects:

| Project | Location | Stack |
|---|---|---|
| Airline Catering Delivery Slip | `/` (root) | Static HTML/CSS/JS |
| Madrid Property Tracker | `/madrid-tracker/` | Python · FastAPI · PostgreSQL · GitHub Actions |

---

## Architecture — Madrid Property Tracker

```
GitHub Actions (cron every 4h)
    └── scanner/scanner.py
          ├── Calls Idealista API (OAuth2)
          ├── Writes new listings → Neon PostgreSQL
          └── Sends Slack alerts (optional)

Railway (always-on)
    └── api/main.py (FastAPI)
          └── Reads Neon PostgreSQL
          └── Serves JSON to dashboard

GitHub Pages
    └── madrid-tracker/dashboard/index.html
          └── Fetches from Railway API
```

---

## Environment Variables

### API (`madrid-tracker/api/.env`)
```
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
IDEALISTA_API_KEY=...
IDEALISTA_SECRET=...
CORS_ORIGINS=http://127.0.0.1:5500,https://sfm7.github.io
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...   # optional
DASHBOARD_URL=https://sfm7.github.io/madrid-tracker/dashboard/index.html
```

### Scanner (`madrid-tracker/scanner/.env`)
```
DATABASE_URL=...
IDEALISTA_API_KEY=...
IDEALISTA_SECRET=...
SLACK_WEBHOOK_URL=...  # optional
```

### GitHub Actions Secrets (repo Settings → Secrets)
```
IDEALISTA_API_KEY
IDEALISTA_SECRET
DATABASE_URL
SLACK_WEBHOOK_URL   # optional
```

---

## Local Development

### Start API
```bash
cd madrid-tracker/api
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uvicorn main:app --reload --port 8000
# Docs at http://localhost:8000/docs
```

### Run Scanner (one shot)
```bash
cd madrid-tracker/scanner
source .venv/bin/activate
python scanner.py
```

### Open Dashboard
- Right-click `madrid-tracker/dashboard/index.html` → **Open with Live Server**
- URL: `http://127.0.0.1:5500/madrid-tracker/dashboard/index.html`
- Change `API_BASE` in the HTML to `http://localhost:8000` for local API

---

## Database (Neon PostgreSQL)

### Key tables
- `properties` — all listings scraped from Idealista
- `price_history` — every price change per property
- `scan_logs` — audit trail per scanner run

### Useful queries
```sql
-- Latest listings
SELECT * FROM properties ORDER BY first_seen_at DESC LIMIT 20;

-- Price drops
SELECT * FROM v_properties_with_drop ORDER BY price_drop_pct DESC;

-- Scanner health
SELECT * FROM scan_logs ORDER BY started_at DESC LIMIT 5;
```

---

## Key Files

| File | Purpose |
|---|---|
| `madrid-tracker/api/main.py` | FastAPI app — all endpoints |
| `madrid-tracker/api/database.py` | DB connection pool |
| `madrid-tracker/scanner/scanner.py` | Idealista scraper + Slack alerts |
| `madrid-tracker/dashboard/index.html` | Frontend (Tailwind + Leaflet + Chart.js) |
| `setup_db.sql` | DB schema — run once on Neon |
| `.github/workflows/scan_madrid.yml` | GitHub Actions cron job |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/properties` | List properties (filterable) |
| GET | `/properties/{id}` | Single property detail |
| GET | `/properties/{id}/history` | Price history |
| GET | `/stats` | Aggregate stats |
| GET | `/health` | Health check |

---

## Deployment

| Component | Platform | How |
|---|---|---|
| Dashboard | GitHub Pages | Push to `main` → auto-deploy |
| API | Railway | Push to `main` → auto-deploy via Procfile |
| Scanner | GitHub Actions | Runs every 4h or manual trigger |

---

## Git Branch Convention

- `main` — production (GitHub Pages + Railway auto-deploy)
- `claude/<feature>-<id>` — Claude Code feature branches
- Always PR → `main`, never force-push `main`

---

## Code Style

- Python: PEP 8, f-strings, type hints on public functions
- JS/HTML: vanilla JS preferred, no build step for dashboard
- Keep scanner.py stateless — all state lives in the DB
- Never hardcode secrets — always use `.env` / GitHub Secrets
