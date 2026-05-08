# 03 - Building Your Exporter

Once `discover.py` confirms you can read the table you want, building
the actual exporter is mostly editing `app/config.py` and
`app/enrichment.py`.

## The pull -> enrich -> write pipeline

`app/exporter.py` orchestrates three steps:

1. **Pull** - run a SELECT against Sage. Lives in `pull()`.
2. **Enrich** - apply your business rules. Lives in `enrichment.py`.
3. **Write** - save to a destination. Lives in `write_csv()` (or your replacement).

Keeping these separate means you can swap any one without touching
the others.

## Step 1: Configure the pull

Edit `app/config.py`:

```python
SAGE_TABLE = "MASTER_PJM_JOB"
SAGE_COLUMNS = ["Job", "Description", "Status", "Address_1", "City", "State", "Postal_Code"]
SAGE_WHERE = None    # or "Status = 'In Progress'", but see warning below
```

> **Filter in Python, not SQL, when in doubt.** Timberline's SQL
> dialect is finicky about quoted strings, case sensitivity, and
> NULL handling. It is almost always safer to pull a wider set and
> filter in `enrichment.py`. The driver is fast enough that pulling
> a few thousand extra rows is cheaper than debugging a malformed
> WHERE clause for an hour.

Always list `SAGE_COLUMNS` explicitly - some Timberline tables have
250+ columns and `SELECT *` is much slower.

## Step 2: Write your enrichment

Open `app/enrichment.py`. The default `enrich_row()` just trims
whitespace. Add whatever you need:

```python
def enrich_row(row: dict) -> dict:
    out = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

    # Parse a job number like "9-260022-61" into business unit + division
    job = out.get("Job", "")
    parts = job.split("-")
    if len(parts) == 3:
        out["Business_Unit"] = parts[0]
        out["Division"] = parts[2]

    # Convert Sage status string to a boolean
    status = (out.get("Status") or "").strip().lower()
    out["Is_Active"] = status in ("in progress", "unstarted")

    return out
```

Keep this code free of side effects so you can unit-test it without
hitting Sage.

## Step 3: Choose an output

The default `write_csv()` writes a UTF-8-with-BOM CSV that opens
cleanly in Excel. Common alternatives:

### Multiple CSVs grouped by some field
```python
from collections import defaultdict

def run_export():
    rows = enrich(pull())
    by_division = defaultdict(list)
    for r in rows:
        by_division[r.get("Division", "_unknown")].append(r)
    for div, group in by_division.items():
        write_csv(group, config.OUTPUT_DIR / f"{div}_jobs.csv")
```

### SQLite database
```python
import sqlite3
def write_sqlite(rows, db_path):
    conn = sqlite3.connect(db_path)
    cols = list(rows[0].keys())
    conn.execute(f"CREATE TABLE IF NOT EXISTS jobs ({','.join(cols)})")
    conn.execute("DELETE FROM jobs")
    placeholders = ",".join("?" * len(cols))
    conn.executemany(
        f"INSERT INTO jobs VALUES ({placeholders})",
        [[r.get(c) for c in cols] for r in rows],
    )
    conn.commit()
    conn.close()
```

### Webhook / HTTP POST
```python
import requests
def post_to_webhook(rows, url):
    requests.post(url, json={"rows": rows}, timeout=30).raise_for_status()
```

### Network share
Just make `config.OUTPUT_DIR` a UNC path - the default writer handles
that fine, as long as the service account has write permission.

```python
OUTPUT_DIR = Path(r"\\pitsrv09\swap\Job List")
```

## Step 4: Test it

```powershell
& "C:\Python311-32\python.exe" -m app.exporter
```

Output goes to `instance/output/` and `instance/logs/exporter.log`.

## Step 5: Repeat for additional tables

If you need data from multiple tables, the cleanest pattern is one
exporter per table - each with its own `app/exporter.py` style module.
Resist the urge to JOIN across Timberline tables in SQL; it works
sometimes, fails inscrutably other times. Pull each table separately
and merge in Python:

```python
def pull():
    jobs = sage_query.select(table="MASTER_PJM_JOB", columns=[...])
    div_idx = {d["Division"]: d for d in sage_query.select(
        table="MASTER_GLM_DIVISION_1", columns=["Division", "Description"])}
    for j in jobs:
        d = div_idx.get(j.get("Division"))
        j["Division_Name"] = d["Description"] if d else None
    return jobs
```

---
Next: [`04-deploy-as-service.md`](04-deploy-as-service.md)
