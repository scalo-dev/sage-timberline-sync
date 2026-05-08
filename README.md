# Sage / Timberline Sync Guide

A reusable, opinionated template for pulling data out of Sage 300 CRE
(Timberline) into anything else — CSV files, SQLite, a Postgres warehouse,
an internal web app, etc.

This is the **second** version of this guide. The original `sage-sync-guide`
relied on a Microsoft Access `.mdb` file with linked tables as a middleman.
That works, but it's fragile and has many moving parts. This version goes
**direct** to the Sage Pervasive ODBC driver from 32-bit Python — fewer
moving parts, easier to debug, easier to deploy.

---

## Why a guide and not a library?

Every Sage installation is slightly different:
- Different DSN names per server
- Different company / data folder paths
- Different module licenses (PJM, JCM, GLM, APM, etc.)
- Different table column subsets per version
- Different status values, naming conventions, custom fields

A drop-in library would lie to you. A guide + a working template you can
fork is more honest. Copy `template/`, run `discover.py` against your DSN,
edit `config.py`, and you have a custom integration in an hour.

---

## What's in this repo

```
sage_sync/
├── README.md                 # you are here
├── docs/                     # chapter-by-chapter guide
│   ├── 01-prerequisites.md
│   ├── 02-discover-connection.md     # READ THIS FIRST
│   ├── 03-build-exporter.md
│   ├── 04-deploy-as-service.md
│   ├── 05-add-flask-ui.md            # optional
│   ├── 06-troubleshooting.md
│   └── reference/
│       ├── timberline-connection-params.md
│       ├── timberline-common-tables.md
│       └── extracting-conn-from-access.md
├── template/                 # copy this folder to start a new project
│   ├── app/
│   │   ├── config.py         # ALL knobs in one place
│   │   ├── connection.py     # connection-string builder (the key file)
│   │   ├── credentials.py    # UID/PWD loader
│   │   ├── sage_query.py     # query helpers
│   │   ├── enrichment.py     # stub for your business logic
│   │   └── exporter.py       # full pull/transform/write skeleton
│   ├── instance/
│   │   └── sage_credentials.ini.example
│   ├── discover.py           # ALWAYS run this first on a new server
│   ├── requirements.txt
│   ├── .gitignore
│   └── README.md
└── service/                  # optional: NSSM helpers if you want it
    ├── run_service.py        #   to run as a Windows service
    ├── install_service.ps1
    └── uninstall_service.ps1
```

---

## The 30-second mental model

```
+---------------------+      ODBC      +-----------------+      Python     +-----------------+
|  Sage / Timberline  | <----------->  |  pyodbc         | <-----------> |  Your script    |
|  (Pervasive on the  |  32-bit DSN +  |  (32-bit Python |  enrich/      |  CSV / SQLite / |
|   Sage server)      |  4 magic params|   on YOUR box)  |  filter/save  |  webhook / etc  |
+---------------------+                +-----------------+                +-----------------+
```

The "magic params" are the four Timberline-specific ODBC connection-string
parameters that, in our experience, are the difference between **all your
tables being invisible** and **everything Just Working**:

```
DatabaseType=1
DBQ=\\Server\TIMBERLINE OFFICE\Data\<Company>\
DictionaryMode=0
StandardMode=0
ShortenNames=0
MaxColSupport=255
```

If you only remember one thing from this guide, remember those four.

---

## Quickstart

```powershell
# 1. Copy the template into a new project folder
Copy-Item -Recurse template C:\Path\To\MyNewIntegration
cd C:\Path\To\MyNewIntegration

# 2. Set up 32-bit Python and install deps
& "C:\Python311-32\python.exe" -m pip install -r requirements.txt

# 3. Create your credentials file (UID/PWD only)
Copy-Item instance\sage_credentials.ini.example instance\sage_credentials.ini
notepad instance\sage_credentials.ini

# 4. Edit app/config.py - set DSN, data folder, table names

# 5. Run discovery to confirm the connection works
& "C:\Python311-32\python.exe" discover.py

# 6. Run your exporter
& "C:\Python311-32\python.exe" -m app.exporter
```

If step 5 prints `EXISTS:` next to your tables, you're good. If not, see
`docs/06-troubleshooting.md`.

---

## Where to go next

| If you want to... | Read |
|---|---|
| Set up a fresh server from scratch | [`docs/01-prerequisites.md`](docs/01-prerequisites.md) |
| Figure out the right connection string | [`docs/02-discover-connection.md`](docs/02-discover-connection.md) |
| Build a custom exporter | [`docs/03-build-exporter.md`](docs/03-build-exporter.md) |
| Run it 24/7 as a Windows service | [`docs/04-deploy-as-service.md`](docs/04-deploy-as-service.md) |
| Add a web UI for users to browse / search / export | [`docs/05-add-flask-ui.md`](docs/05-add-flask-ui.md) |
| Debug something that's not working | [`docs/06-troubleshooting.md`](docs/06-troubleshooting.md) |
| Look up table names or connection-string params | [`docs/reference/`](docs/reference/) |

---

## Credits

This guide is the result of a lot of trial-and-error against a real Sage 300
CRE installation. Every "gotcha" in `06-troubleshooting.md` was a
two-hour-debugging-session at some point.
