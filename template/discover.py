"""
Sage / Timberline ODBC discovery tool.

Run this FIRST against any new DSN to confirm:
  1. The connection itself works (DSN, UID, PWD)
  2. You're using the right combination of DatabaseType + DBQ + extras
  3. The tables you want actually exist and are visible
  4. The columns you expect are actually there

Why this script exists: Sage Timberline's tsODBC driver silently hides
tables when the connection-string parameters are wrong. You'll get
"Table or view not found" errors that look identical to a missing
permission OR a missing table OR a wrong DatabaseType. The only way to
tell them apart is to systematically vary parameters and probe.

Usage:
  C:\\Python311-32\\python.exe discover.py
  C:\\Python311-32\\python.exe discover.py --tables MASTER_PJM_JOB MASTER_GLM_DIVISION_1
  C:\\Python311-32\\python.exe discover.py --uid OTHERUSER --pwd OTHERPWD

Output is mirrored to discover_output.txt next to this script so you can
review it after the console window closes.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from app import config
from app.connection import build_connection_string
from app.credentials import load_credentials


# ---------------------------------------------------------------------------
# Output mirror: print() goes to both console and a file
# ---------------------------------------------------------------------------
_LOG_PATH = Path(__file__).resolve().parent / "discover_output.txt"
_LOG_FH = open(_LOG_PATH, "w", encoding="utf-8")


class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            try:
                st.write(s)
                st.flush()
            except Exception:
                pass

    def flush(self):
        for st in self.streams:
            try:
                st.flush()
            except Exception:
                pass


sys.stdout = _Tee(sys.__stdout__, _LOG_FH)
sys.stderr = _Tee(sys.__stderr__, _LOG_FH)


# ---------------------------------------------------------------------------
# A handful of well-known Timberline tables to probe by default. These are
# usually present in any company that licenses the corresponding module.
# Override with --tables on the command line.
# ---------------------------------------------------------------------------
DEFAULT_TABLES = [
    "MASTER_PJM_JOB",            # Project Management - jobs
    "MASTER_JCM_JOB_1",          # Job Cost - jobs (master record)
    "MASTER_JCM_JOB_2",          # Job Cost - financial totals
    "MASTER_GLM_DIVISION_1",     # General Ledger - divisions
    "MASTER_PRM_EMPLOYEE",       # Payroll - employees
    "MASTER_APM_VENDOR",         # AP - vendors
    "MASTER_ARM_CUSTOMER",       # AR - customers
]


def probe(uid: str, pwd: str, db_type, data_folder, extras, tables) -> None:
    import pyodbc

    label = (
        f"DSN={config.ODBC_DSN!r}  DatabaseType={db_type}  "
        f"DBQ={data_folder!r}  extras={'+'.join(extras.keys()) if extras else 'none'}"
    )
    print("\n" + "=" * 78)
    print(label)
    print("=" * 78)

    conn_str = build_connection_string(
        uid=uid,
        pwd=pwd,
        dsn=config.ODBC_DSN,
        database_type=db_type,
        data_folder=data_folder,
        extras=extras,
    )

    t0 = time.time()
    try:
        conn = pyodbc.connect(conn_str, autocommit=True, timeout=15)
    except Exception as e:
        print(f"  CONNECT FAILED in {time.time()-t0:.1f}s: {str(e)[:200]}")
        return
    print(f"  connected in {time.time()-t0:.1f}s")

    try:
        try:
            print(f"  database: {conn.getinfo(pyodbc.SQL_DATABASE_NAME)}")
            print(f"  driver:   {conn.getinfo(pyodbc.SQL_DRIVER_NAME)}")
        except Exception:
            pass
        try:
            conn.timeout = 15
        except Exception:
            pass

        cur = conn.cursor()
        any_found = False
        for t in tables:
            try:
                cur.execute(f"SELECT TOP 1 * FROM {t}")
                cur.fetchone()
                cols = [c[0] for c in cur.description] if cur.description else []
                any_found = True
                print(f"  EXISTS: {t}  ({len(cols)} cols)")
                # Print ALL columns, 6 per line, so nothing important hides.
                for i in range(0, len(cols), 6):
                    print("          " + ", ".join(cols[i:i + 6]))
            except Exception as e:
                msg = str(e).split("\n")[0]
                if "Table or view not found" in msg:
                    print(f"  ----- : {t}  (not visible / not found)")
                else:
                    print(f"  ERROR : {t} -> {msg[:200]}")

        if not any_found:
            print("  >>> No probed tables visible with this configuration <<<")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--tables",
        nargs="+",
        default=DEFAULT_TABLES,
        help="Table names to probe (default: a handful of common Timberline tables)",
    )
    ap.add_argument(
        "--uid",
        default=None,
        help="Override UID (default: from sage_credentials.ini)",
    )
    ap.add_argument(
        "--pwd",
        default=None,
        help="Override PWD (default: from sage_credentials.ini)",
    )
    args = ap.parse_args()

    if args.uid and args.pwd:
        uid, pwd = args.uid, args.pwd
        print("(using UID/PWD from command line)")
    else:
        uid, pwd = load_credentials()

    folder = config.SAGE_DATA_FOLDER
    extras = dict(config.SAGE_EXTRA_PARAMS)

    print(f"DSN: {config.ODBC_DSN}")
    print(f"Probing {len(args.tables)} table(s):")
    for t in args.tables:
        print(f"  - {t}")

    # Probe order: best-guess first, then strip parts to identify which
    # parameter is critical when something fails.
    probe(uid, pwd, db_type=1, data_folder=folder, extras=extras, tables=args.tables)
    probe(uid, pwd, db_type=1, data_folder=folder, extras=None,   tables=args.tables)
    probe(uid, pwd, db_type=1, data_folder=None,   extras=extras, tables=args.tables)
    probe(uid, pwd, db_type=None, data_folder=folder, extras=extras, tables=args.tables)
    probe(uid, pwd, db_type=2, data_folder=folder, extras=extras, tables=args.tables)

    print("\n" + "=" * 78)
    print("DONE")
    print("=" * 78)
    print("Look at the FIRST section that shows EXISTS for the table you want.")
    print("That's the combination your config.py should match.")
    return 0


if __name__ == "__main__":
    rc = 0
    try:
        rc = main()
    except Exception:
        import traceback
        print("\n!!! UNCAUGHT EXCEPTION !!!")
        traceback.print_exc()
        rc = 99
    finally:
        print(f"\n[ Output also saved to: {_LOG_PATH} ]")
        try:
            _LOG_FH.close()
        except Exception:
            pass
        try:
            input("\nPress Enter to close...")
        except EOFError:
            pass
    sys.exit(rc)
