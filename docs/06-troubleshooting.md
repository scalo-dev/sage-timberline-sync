# 06 - Troubleshooting

Every entry here represents a real debugging session. Check the
symptom column first.

---

### "Architecture mismatch between the Driver and Application"

You're running 64-bit Python. The Pervasive driver is 32-bit.

```powershell
python -c "import struct; print(struct.calcsize('P') * 8)"
```
Must print `32`. If it prints `64`, install 32-bit Python (see
[`01-prerequisites.md`](01-prerequisites.md)) and use that interpreter
explicitly:
```powershell
& "C:\Python311-32\python.exe" -m pip install -r requirements.txt
& "C:\Python311-32\python.exe" -m app.exporter
```

---

### "Data source name not found and no default driver specified"

The DSN string doesn't match a registered DSN.

1. Open `C:\Windows\SysWOW64\odbcad32.exe` (the **32-bit** ODBC
   manager).
2. Look at System DSN tab.
3. Copy the DSN name **exactly**, including spaces and capitalization,
   into `app/config.py` `ODBC_DSN`.

Common gotcha: the same Sage data folder is often exposed under
different DSN names on different machines. Don't assume your laptop's
DSN name matches the server's.

---

### "Table or view not found" but the table exists in Access

Almost always: missing `SAGE_EXTRA_PARAMS` in your connection string.

Confirm by running:
```powershell
& "C:\Python311-32\python.exe" discover.py
```
Compare the section labelled `extras=DictionaryMode+...` against the
section labelled `extras=none`. If the first finds the table and the
second doesn't, those extras are mandatory for your installation -
make sure they're in `config.SAGE_EXTRA_PARAMS`.

Other less-likely causes:
- Wrong `DatabaseType` (try `1` and `2`)
- Wrong `DBQ` data folder path (forgot the trailing backslash?)
- Sage user genuinely doesn't have read on this module
- The module isn't licensed for this company

---

### Query returns zero rows from a populated table

Suspect the WHERE clause first. Comment it out (`SAGE_WHERE = None`)
and see if rows come back. If they do:
- Check string quoting - Sage often wants `'value'` (single quotes)
- Check case sensitivity - try `Status = 'In Progress'` vs
  `'IN PROGRESS'` vs trimmed comparisons in Python
- Check NULLs - `Status = ''` does not match `Status IS NULL`

Easier: pull everything and filter in Python.

---

### "discover.py is hanging"

It's calling something that enumerates Pervasive metadata - either
`cursor.tables()` or a SELECT on a too-wide table. The shipped
discovery script avoids both, but if you've modified it:

- Never call `cursor.tables()` against Pervasive
- Always `SELECT TOP 1 *` first to confirm the table responds
- Set `cursor.timeout = 15` so a slow query gives up

---

### Service installs but immediately enters SERVICE_PAUSED

Read `instance\logs\stderr.log`. The most common content is:

```
C:\Python311-32\python.exe: can't open file 'C:\Path': [Errno 2] No such file or directory
```

NSSM's `AppParameters` was stored unquoted, so a project path
containing a space (e.g. `C:\Job List\run_service.py`) was parsed as
two arguments. Re-run the installer - the shipped `install_service.ps1`
sets `AppParameters` with explicit quotes.

If you set NSSM up by hand, fix it with:
```powershell
nssm set SageExporter AppParameters "`"C:\Path with space\run_service.py`""
nssm restart SageExporter
```

---

### Service runs locally but fails on the server with "Sage credentials file not found"

You're running the script from a different working directory than the
project root. NSSM is fine because `install_service.ps1` sets
`AppDirectory`, but if you're invoking from Task Scheduler or by hand:

```powershell
cd C:\Path\To\Project
& "C:\Python311-32\python.exe" -m app.exporter
```

`config.CREDENTIALS_FILE` is computed relative to the project root, so
the cwd matters.

---

### CSV opens with garbled accented characters in Excel

The default writer uses UTF-8 with BOM (`encoding="utf-8-sig"`), which
Excel reads correctly. If you've changed it to `"utf-8"` plain, Excel
will mangle non-ASCII. Switch back.

---

### "Permission denied" writing to network share

The service account can't write there. NSSM defaults to `LocalSystem`,
which has no network identity.

- `nssm edit SageExporter` -> **Log on** tab -> "This account" -> a
  domain account that has write permission on the share.
- Restart the service.

---

### Logs say `pip install` failed during install

Usually pip can't reach PyPI from the server (firewall) or the
`requirements.txt` references a wheel that isn't built for 32-bit
Python.

```powershell
& "C:\Python311-32\python.exe" -m pip install pyodbc==5.1.0
```
If this fails by itself, it's a network/proxy issue, not a code issue.

---

### Where to look first when something breaks

Order of suspicion, in our experience:

1. The connection string parameters changed (someone "tidied up" the DSN)
2. The Sage user's password expired
3. The Pervasive engine is down (restart from Sage Desktop)
4. Network share unreachable from the service account
5. Disk full on the server
6. Actually a bug in your code

---
Reference docs: [`reference/`](reference/)
