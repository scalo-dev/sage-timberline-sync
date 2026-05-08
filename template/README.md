# Template: Sage / Timberline Exporter

A working starter project. Copy this whole folder, customize `app/config.py`,
and you have a Sage exporter.

## Files

| File | Edit when... |
|---|---|
| `app/config.py` | Always (DSN, data folder, table, columns) |
| `app/credentials.py` | Probably never |
| `app/connection.py` | Probably never (the magic is here) |
| `app/sage_query.py` | When you need fancier queries |
| `app/enrichment.py` | Always (your business logic) |
| `app/exporter.py` | When you need a different output (SQLite, webhook, etc.) |
| `discover.py` | Run unchanged when wiring up a new server |

## First-time setup

```powershell
# 1. Install 32-bit Python 3.11+ on the server (Pervasive driver is 32-bit)
# 2. pip install
& "C:\Python311-32\python.exe" -m pip install -r requirements.txt

# 3. Credentials
Copy-Item instance\sage_credentials.ini.example instance\sage_credentials.ini
notepad instance\sage_credentials.ini

# 4. Edit app/config.py - at minimum: ODBC_DSN, SAGE_DATA_FOLDER, SAGE_TABLE, SAGE_COLUMNS

# 5. Confirm the connection works
& "C:\Python311-32\python.exe" discover.py

# 6. Run the exporter
& "C:\Python311-32\python.exe" -m app.exporter
```

The first run writes to `instance/output/<tablename>.csv`. Logs go to
`instance/logs/exporter.log`.

## Customizing

### Different output format (SQLite, Postgres, webhook, etc.)
Replace `write_csv()` in `app/exporter.py` with whatever you want.
Keep `pull()` and `enrich()` the same.

### Multi-table pull
Override `pull()` to call `sage_query.select(table=...)` multiple times
and merge in Python. Avoid SQL JOINs against Timberline - the dialect
is finicky.

### Run on a schedule
See `../service/` in the parent guide for NSSM service setup, or just
schedule with Task Scheduler:

```
Program: C:\Python311-32\python.exe
Arguments: -m app.exporter
Start in: C:\Path\To\This\Project
```

### Add a web UI for users
See `docs/05-add-flask-ui.md` in the parent guide.
