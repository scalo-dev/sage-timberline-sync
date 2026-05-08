"""
Sage / Timberline ODBC connection-string builder.

This is the most important file in the project. The default values come
straight from a working Access "Linked Table Manager" connection string.
If anything else is wrong, things explode in confusing ways - tables
appear empty, columns are missing, queries silently return nothing.

See docs/02-discover-connection.md for the full story.
"""
from __future__ import annotations

from typing import Mapping, Optional

from . import config


def build_connection_string(
    uid: str,
    pwd: str,
    *,
    dsn: Optional[str] = None,
    database_type: Optional[int] = ...,
    data_folder: Optional[str] = ...,
    extras: Optional[Mapping[str, str]] = ...,
) -> str:
    """Build a pyodbc connection string for the Sage Timberline driver.

    Arguments default to whatever's in config.py. Pass explicit values
    to override (used by discover.py to test variations).

    The sentinel `...` means "use the config default"; pass `None`
    explicitly to omit a parameter from the connection string.
    """
    if dsn is None:
        dsn = config.ODBC_DSN
    if database_type is ...:
        database_type = config.SAGE_DATABASE_TYPE
    if data_folder is ...:
        data_folder = config.SAGE_DATA_FOLDER
    if extras is ...:
        extras = config.SAGE_EXTRA_PARAMS

    parts = [f"DSN={dsn}", f"UID={uid}", f"PWD={pwd}"]
    if database_type is not None:
        parts.append(f"DatabaseType={database_type}")
    if data_folder:
        parts.append(f"DBQ={data_folder}")
    if extras:
        for k, v in extras.items():
            parts.append(f"{k}={v}")
    return ";".join(parts)


def open_connection():
    """Open and return a live pyodbc connection using config defaults."""
    import pyodbc  # imported lazily so this module can be inspected without ODBC

    from .credentials import load_credentials

    uid, pwd = load_credentials()
    return pyodbc.connect(build_connection_string(uid, pwd), autocommit=True)
