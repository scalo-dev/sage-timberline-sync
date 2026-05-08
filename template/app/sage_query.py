"""
Thin query helpers on top of pyodbc.

Returns plain dicts (column name -> value) so downstream code never has
to think about cursor positions or column indexes.
"""
from __future__ import annotations

import logging
from typing import Iterable, Optional

from . import config
from .connection import open_connection

log = logging.getLogger(__name__)


def query(sql: str, params: Iterable = ()) -> list[dict]:
    """Run sql and return one dict per row."""
    log.info("Query: %s", sql)
    conn = open_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, *params) if params else cur.execute(sql)
        col_names = [c[0] for c in cur.description] if cur.description else []
        out: list[dict] = []
        for raw in cur.fetchall():
            out.append({col_names[i]: raw[i] for i in range(len(col_names))})
        return out
    finally:
        conn.close()


def select(
    table: Optional[str] = None,
    columns: Optional[list[str]] = None,
    where: Optional[str] = None,
) -> list[dict]:
    """Convenience: SELECT <columns> FROM <table> [WHERE ...].

    Defaults to config.SAGE_TABLE / SAGE_COLUMNS / SAGE_WHERE.
    """
    table = table or config.SAGE_TABLE
    columns = columns or config.SAGE_COLUMNS
    where = where if where is not None else config.SAGE_WHERE

    cols_sql = ", ".join(columns) if columns else "*"
    sql = f"SELECT {cols_sql} FROM {table}"
    if where:
        sql += f" WHERE {where}"
    return query(sql)
