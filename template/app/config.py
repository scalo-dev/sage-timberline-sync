"""
Project configuration.

Every adjustable knob lives here. Edit this file when adapting the
template to a new server, table, or business need. Don't sprinkle
hardcoded values across the rest of the code.
"""
from __future__ import annotations
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTANCE_DIR = PROJECT_ROOT / "instance"
LOGS_DIR = INSTANCE_DIR / "logs"
CREDENTIALS_FILE = INSTANCE_DIR / "sage_credentials.ini"

# Where to write any files this exporter produces. Adjust to taste.
OUTPUT_DIR = INSTANCE_DIR / "output"

# ---------------------------------------------------------------------------
# Sage / Timberline ODBC connection
# ---------------------------------------------------------------------------
# 1. The DSN as it appears in the SERVER's 32-bit ODBC manager
#    (C:\Windows\SysWOW64\odbcad32.exe). DSN names commonly differ
#    between machines - the same Sage data folder might be exposed as
#    "ISD The Scalo Group of-103285019" on the server but
#    "SCALO COMPANIES" on a developer's laptop.
ODBC_DSN = "REPLACE_WITH_YOUR_DSN"

# 2. The Timberline data folder. Get this from the DSN configuration in
#    the 32-bit ODBC manager, or from an existing Access linked-table
#    connection string. The TRAILING BACKSLASH IS REQUIRED.
SAGE_DATA_FOLDER: str | None = r"\\YourSageServer\TIMBERLINE OFFICE\Data\YourCompany\\"

# 3. DatabaseType. Almost always 1 in modern Timberline. Set to None
#    only if you've tested without it and confirmed it's unnecessary.
SAGE_DATABASE_TYPE: int | None = 1

# 4. The four "magic" extra parameters. Without these (in particular
#    DictionaryMode and StandardMode), the driver will silently hide
#    JCM/PJM/most module tables. These values are what Access uses
#    when you create a linked table - DO NOT change them unless you
#    know what you're doing.
SAGE_EXTRA_PARAMS: dict[str, str] = {
    "DictionaryMode": "0",
    "MaxColSupport": "255",
    "ShortenNames": "0",
    "StandardMode": "0",
}

# ---------------------------------------------------------------------------
# What to pull
# ---------------------------------------------------------------------------
# The Sage table to query. Change this for your use case. Use
# discover.py to confirm it's visible and what columns it has.
SAGE_TABLE = "MASTER_PJM_JOB"

# Columns to SELECT. Listing them explicitly is much faster than
# SELECT * for wide tables (some Timberline tables have 250+ columns).
SAGE_COLUMNS: list[str] = [
    "Job",
    "Description",
    "Status",
]

# Optional: a WHERE clause appended to the SELECT. Leave None to pull
# everything and filter in Python (often safer because Timberline's
# SQL flavor is finicky about expressions).
SAGE_WHERE: str | None = None
