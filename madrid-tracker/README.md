# Madrid Property Tracker

Personal real-estate opportunity scanner for Madrid using the Idealista API,
Neon PostgreSQL, and a custom dashboard hosted on GitHub Pages.

## Architecture

```
GitHub Actions (cron every 4h)
        │
        ▼
  scanner/scanner.py  ──────►  Neon PostgreSQL
                                    │
                                    ▼
                           api/main.py (FastAPI)
                           deployed on Railway
                                    │
                                    ▼
                    dashboard/index.html  (GitHub Pages)
                    sfm7.github.io/madrid-tracker/dashboard/
```

## Why not Power BI?

| Feature              | Power BI             | This dashboard           |
|----------------------|----------------------|--------------------------|
| Cost                 | Pro licence required | Free                     |
| Custom actions       | Very limited         | Mark viewed, save, notes |
| Real-time data       | Scheduled refresh    | On-demand + auto-scan    |
| Hosting              | Microsoft cloud      | Your own GitHub Pages    |
| Price history chart  | Complex setup        | Built-in per property    |
| Map view             | Paid add-on          | Free (OpenStreetMap)     |

---

## Setup Instructions

### 1. Idealista API credentials

1. Register at https://developers.idealista.com/
2. Create an app → get your **API Key** and **Secret**

### 2. Neon database

1. Sign up at https://neon.tech (free tier is plenty)
2. Create a project named `madrid-tracker`
3. Copy your **connection string** (looks like `postgresql://user:pass@host.neon.tech/dbname?sslmode=require`)
4. Run the schema:

```bash
psql "YOUR_DATABASE_URL" -f madrid-tracker/setup_db.sql
```

### 3. GitHub repository secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret name          | Value                              |
|----------------------|------------------------------------|
| `IDEALISTA_API_KEY`  | Your Idealista API key             |
| `IDEALISTA_SECRET`   | Your Idealista secret              |
| `DATABASE_URL`       | Your Neon connection string        |

Optional repository **Variables** (Settings → Variables → Actions):

| Variable name          | Default | Example                |
|------------------------|---------|------------------------|
| `SCAN_OPERATION`       | `sale`  | `rent`                 |
| `SCAN_PROPERTY_TYPE`   | `homes` | `homes`                |
| `SCAN_DISTANCE_KM`     | `15`    | `10`                   |
| `SCAN_MIN_PRICE`       | (none)  | `200000`               |
| `SCAN_MAX_PRICE`       | (none)  | `800000`               |
| `SCAN_MIN_ROOMS`       | (none)  | `2`                    |
| `SCAN_MIN_SIZE`        | (none)  | `60`                   |

The scanner will run automatically every 4 hours via GitHub Actions.
To scan immediately: **Actions → Madrid Property Scanner → Run workflow**.

### 4. Deploy the FastAPI backend (Railway)

1. Install the Railway CLI: https://docs.railway.app/develop/cli
2. From the `madrid-tracker/api/` directory:

```bash
cd madrid-tracker/api
railway login
railway init          # create a new Railway project
railway up            # deploy

# Set environment variables in Railway dashboard:
# DATABASE_URL, IDEALISTA_API_KEY, IDEALISTA_SECRET, CORS_ORIGINS
```

3. Note the Railway app URL (e.g. `https://madrid-tracker-api.railway.app`)

### 5. Connect the dashboard to your API

Edit `madrid-tracker/dashboard/index.html` line ~210:

```js
const API_BASE = "https://YOUR-RAILWAY-APP.railway.app";
//                        ↑ replace with your Railway URL
```

The dashboard is then accessible at:
`https://sfm7.github.io/madrid-tracker/dashboard/`

---

## Local Development

### Run the scanner locally

```bash
cd madrid-tracker/scanner
pip install -r requirements.txt

export IDEALISTA_API_KEY=your_key
export IDEALISTA_SECRET=your_secret
export DATABASE_URL=postgresql://...

python scanner.py
```

### Run the API locally

```bash
cd madrid-tracker/api
pip install -r requirements.txt

cp .env.example .env
# edit .env with your credentials

uvicorn main:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

### View the dashboard locally

Open `madrid-tracker/dashboard/index.html` in a browser.
Change `API_BASE` to `http://localhost:8000` while developing.

---

## Dashboard Features

| Feature              | Description                                       |
|----------------------|---------------------------------------------------|
| KPI bar              | Active listings, new in 48h, unseen, saved, drops |
| Filter tabs          | All / New 48h / Saved / Price drop / Unseen       |
| Filters              | District, price range, rooms, sort                |
| Map view             | Price-labelled markers on OpenStreetMap           |
| Property cards       | Photo, price, drop badge, rooms, size, district   |
| Property drawer      | Full details, price history chart, notes, actions |
| Save / Viewed        | Personal tracking flags per property             |
| Notes                | Free-text personal notes per property            |
| Manual scan trigger  | Button in the header                              |

## API Endpoints

| Method | Path                           | Description                    |
|--------|--------------------------------|--------------------------------|
| GET    | `/properties`                  | List with filters & pagination |
| GET    | `/properties/{code}`           | Detail + price history         |
| PATCH  | `/properties/{code}/viewed`    | Toggle viewed                  |
| PATCH  | `/properties/{code}/saved`     | Toggle saved                   |
| PATCH  | `/properties/{code}/notes`     | Update notes                   |
| GET    | `/stats`                       | Dashboard KPIs                 |
| GET    | `/scan-logs`                   | Scanner history                |
| POST   | `/scan/trigger`                | Trigger manual scan            |

Interactive docs available at `YOUR_RAILWAY_URL/docs`

---

## Database Schema

- **`properties`** — one row per property, upserted on each scan
- **`price_history`** — appended whenever price changes (or on first insert)
- **`scan_logs`** — one row per scanner run for auditing
- **`v_properties_with_drop`** — view showing price drop % vs initial price

## Notes

- Idealista API has rate limits and quota restrictions. Check your plan.
- The scanner marks properties as `is_active = FALSE` when they disappear from search results (sold / delisted).
- `price_per_sqm` is a computed column — always up to date.
- All timestamps are stored in UTC.
