# 02 - Discovering the Right Connection String

This is the most important chapter. Read it carefully - it will save
you days.

## The problem

Sage's tsODBC driver does not just have a username, password, and DSN.
It has half a dozen other parameters that fundamentally change what
the driver shows you. With the wrong combination:

- Tables silently disappear (you get `Table or view not found` even
  though the table is right there in Access)
- Columns are renamed or truncated
- Queries return zero rows from a populated table
- Some queries work, others fail with cryptic errors

These failure modes look identical to "the user doesn't have
permission" or "this table doesn't exist on this Sage version" - which
sends you down hours of pointless rabbit holes.

## The four magic parameters

```
DatabaseType=1
DBQ=\\Server\TIMBERLINE OFFICE\Data\<Company>\
DictionaryMode=0
StandardMode=0
ShortenNames=0
MaxColSupport=255
```

These are what Microsoft Access sets when you create a Linked Table to
a Sage company. With these set, **everything works**. Without them,
PJM and JCM tables are usually invisible.

> Don't take our word for it - the discovery script in this template
> will demonstrate it on your specific server.

## How to figure out the right values

### Method A: Steal them from Access (recommended)

If anyone has ever set up Access linked tables against this Sage
company, the connection string is sitting right there. See
[`reference/extracting-conn-from-access.md`](reference/extracting-conn-from-access.md)
for a step-by-step.

### Method B: Run discover.py

The template ships with `discover.py`, which connects with several
common parameter combinations and probes a list of well-known tables.
The first combination that finds your tables is the one to use.

```powershell
cd C:\Path\To\Project
& "C:\Python311-32\python.exe" discover.py
```

It writes output both to the console and to `discover_output.txt` so
you can review it after the window closes.

Look for output like:
```
==============================================================================
DSN='ISD The Scalo...'  DatabaseType=1  DBQ='\\PITSRV08\...\Scalo\'  extras=DictionaryMode+...
==============================================================================
  connected in 0.5s
  EXISTS: MASTER_PJM_JOB  (47 cols)
          Job, Description, Address_1, Address_2, City, State
          Postal_Code, Country, Estimator, Project_Mgr, Status, Type
          ...
```

The first variation that prints `EXISTS` for the table you care about
is your winning combination. Edit `app/config.py` to match.

If **no** variation finds the table:
- The table might not exist for this company / module license
- Your UID might not have read permission
- The DSN might point at a different company than you think
- See [`06-troubleshooting.md`](06-troubleshooting.md)

## Probing other tables

To discover columns of any specific table:
```powershell
& "C:\Python311-32\python.exe" discover.py --tables MASTER_PJM_JOB MASTER_GLM_DIVISION_1
```
The script prints **all** columns - don't trust shorter lists. We've
been bitten more than once by truncated output that made us think a
table was missing fields it actually had.

## Why we don't use cur.tables()

The "right" pyodbc way to enumerate tables is `cursor.tables()`. With
Pervasive, that call can take **minutes** or hang indefinitely on
even a moderately-sized data folder, because it reads metadata for
hundreds of tables and views. The discovery script deliberately
avoids it - direct SELECT probes against named tables are 100x faster
and more informative anyway.

---
Next: [`03-build-exporter.md`](03-build-exporter.md)
