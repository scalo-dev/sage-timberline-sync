# 01 - Prerequisites

Before you can talk to Sage / Timberline from Python, the following must
be in place on the machine that will run your script. This is usually
**not** your dev laptop - it's the application server that already has
Sage Accounting Workstation installed.

## On the Sage server (or any machine running the exporter)

### 1. Sage Accounting Workstation
The Pervasive client and tsODBC driver come bundled. If you can open
"Sage 300 Construction and Real Estate Accounting" on this machine,
the driver is installed.

### 2. The 32-bit Pervasive ODBC driver is registered
Open **`C:\Windows\SysWOW64\odbcad32.exe`** (the 32-bit ODBC manager -
NOT the default `odbcad32.exe` in System32). Look at the **Drivers**
tab. You should see an entry like `Sage Timberline Office tsODBC` or
`Pervasive Software`.

> **The 64-bit ODBC manager will NOT show this driver.** This trips
> people up constantly. Always use the SysWOW64 one.

### 3. A System DSN exists pointing at the company you want
Same SysWOW64 ODBC manager, **System DSN** tab. Note the **DSN name**
exactly - this string goes in `app/config.py` as `ODBC_DSN`.

The DSN's **Configure** button shows the data folder path. Note that
too - it goes into `app/config.py` as `SAGE_DATA_FOLDER`. It will
look something like:
```
\\PITSRV08\TIMBERLINE OFFICE\Data\Scalo\
```
**The trailing backslash is important.**

### 4. 32-bit Python
Install Python 3.11 from python.org, choosing the **32-bit** ("Windows
installer (32-bit)") download. Install to `C:\Python311-32\` to match
the install scripts in this guide.

The Pervasive driver is 32-bit only. Trying to load it from 64-bit
Python gives `Architecture mismatch between the Driver and Application`.

### 5. A Sage SQL user with read access
You need a UID/PWD pair that Sage's "ODBC Security" admin tool will
accept. **This is not the same as a Windows login** - it's a separate
credential set up inside Sage. Ask whoever administers Sage. Read-only
is sufficient for an exporter.

## On your dev machine (optional)

If you want to develop and test from your laptop instead of RDPing into
the server every time:
- Install 32-bit Python the same way
- Install **Sage Accounting Workstation** (full client) on your laptop
- Configure a System DSN in the SysWOW64 ODBC manager pointing at the
  same data folder as the server
- Note: the DSN name on your laptop will probably be different from the
  server's. That's why `ODBC_DSN` is configurable.

## Sanity check

Run this 3-line script to confirm pyodbc can see the driver:

```python
import pyodbc
for d in pyodbc.drivers():
    print(d)
```

You should see a Timberline / Pervasive entry. If you don't, you're
running 64-bit Python.

---
Next: [`02-discover-connection.md`](02-discover-connection.md)
