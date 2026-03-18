# setup

Set up the full Madrid Tracker project from scratch on a new machine.

## Steps

1. Create Python virtual environments and install dependencies:

```bash
cd madrid-tracker/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

cd ../scanner
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

2. Copy env templates:

```bash
cp madrid-tracker/api/.env.example madrid-tracker/api/.env
cp madrid-tracker/api/.env.example madrid-tracker/scanner/.env
```

3. Fill in credentials in both `.env` files:
   - `DATABASE_URL` — from Neon dashboard
   - `IDEALISTA_API_KEY` and `IDEALISTA_SECRET` — from Idealista developer portal
   - `SLACK_WEBHOOK_URL` — optional

4. Verify API starts:

```bash
cd madrid-tracker/api
source .venv/bin/activate
uvicorn main:app --reload --port 8000
```
