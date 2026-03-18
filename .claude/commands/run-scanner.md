# run-scanner

Run the Idealista scanner once locally.

```bash
cd madrid-tracker/scanner && source .venv/bin/activate && python scanner.py
```

Reads `.env` for credentials. Logs new listings and price drops to stdout and writes to the Neon DB.
