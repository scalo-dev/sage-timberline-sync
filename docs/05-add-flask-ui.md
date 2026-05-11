# 05 - Adding a Flask UI (Optional)

If users need to browse, filter, search, or export Sage data
ad-hoc - without waiting for the next CSV refresh - layer a small
Flask app on top of the same exporter.

This chapter sketches the architecture rather than shipping a
template, because the UI specifics depend heavily on what your
users want to do.

## Architecture

```
+------------------------+
| NSSM service           |
|                        |
|  +------------------+  |
|  | Waitress (WSGI)  |  |    HTTP :8765      Browser
|  |   |              | <----------------->  (sortable table,
|  |   v              |  |                    fuzzy search,
|  | Flask app        |  |                    PDF/CSV export)
|  |   - /            |  |
|  |   - /api/data    |  |
|  +------------------+  |
|                        |
|  +------------------+  |
|  | APScheduler      |  |
|  |   every 4h:      |  |
|  |   run_export()   |  |
|  +------------------+  |
+------------------------+
```

A single Python process runs both the web server and the periodic
exporter. They share a `cache.json` (or just an in-memory `dict`)
that the API serves.

## Recommended stack

| Concern | Library |
|---|---|
| WSGI server | **waitress** (`pip install waitress`) - prod-grade, no native deps |
| Web framework | **flask** |
| Scheduling | **apscheduler** |
| Frontend table | Plain HTML + vanilla JS, plus **Fuse.js** for fuzzy search |
| CSV export | Build it client-side from the displayed rows |
| PDF export | **jsPDF** + **jspdf-autotable** (CDN-loaded, no build step) |

Avoid: webpack/Vite/React. The whole point of this UI is to be a
single `index.html` your users open without installing anything.

## Data flow

1. APScheduler fires `run_export()` every N hours. The result is
   written to `instance/output/data.json` (or kept in a module-level
   variable).
2. `GET /api/data` returns the current cached data as JSON.
3. The frontend fetches once on load, then does **all** filtering,
   sorting, and search client-side over the in-memory dataset.
4. Export buttons (CSV, PDF) operate on the currently-visible filtered
   rows, not the full dataset.

This keeps the server stateless and the UI snappy even with thousands
of rows.

## Skeleton run_service.py

```python
from apscheduler.schedulers.background import BackgroundScheduler
from waitress import serve

from app.exporter import run_export
from app.server import create_app   # your Flask factory

def main():
    app = create_app()
    sched = BackgroundScheduler()
    sched.add_job(
        run_export,
        "interval",
        hours=4,
        id="export",
        max_instances=1,
        coalesce=True,
        # If a previous run hung past its window (e.g. Sage was
        # unreachable), drop the queued tick rather than letting
        # max_instances=1 silently skip every subsequent run forever.
        misfire_grace_time=300,
    )
    sched.start()
    run_export()                    # one immediate run on startup
    serve(app, host="0.0.0.0", port=8765)
```

## Useful UI features (from experience)

- **Toggle switches for noisy data**, off by default. e.g. "Show
  closed jobs", "Show service / cost jobs". Users dismiss noise once,
  then forget about it.
- **A "last updated at" timestamp** in the corner. People always ask.
- **Column-header sort** that toggles asc/desc/none on click.
- **Per-column dropdown filters** built from the unique values
  actually present in the data.
- **Fuzzy search across all columns** with Fuse.js - users don't
  remember which column had the substring.
- **Export visible rows**, not all rows. The whole point is for them
  to filter then export.

## DNS / friendly URL

If you want users to type `jobs.app` instead of
`http://10.0.0.9:8765`, add an A record on your internal DNS pointing
`jobs` (in your `app` zone) to the server's IP.

DNS resolves names to IPs only - it does **not** redirect ports.
Options:
- Move the service to port 80 (`serve(app, ..., port=80)`, requires
  the service account to bind low ports - LocalSystem can)
- Run an IIS or nginx reverse proxy on 80 -> 8765
- Tell users to bookmark `jobs.app:8765` and call it a day

---
Next: [`06-troubleshooting.md`](06-troubleshooting.md)
