"""
Business-logic enrichment.

This is where you transform raw Sage rows into whatever shape your
downstream consumers want. A few common patterns are stubbed below;
delete what you don't need.
"""
from __future__ import annotations


def enrich_row(row: dict) -> dict:
    """Transform a single Sage row. Default: pass-through with whitespace stripped."""
    return {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}


def enrich_all(rows: list[dict]) -> list[dict]:
    """Apply enrich_row to every row."""
    return [enrich_row(r) for r in rows]


# ---------------------------------------------------------------------------
# Common patterns - uncomment / adapt as needed
# ---------------------------------------------------------------------------

# def filter_active(rows: list[dict], status_field: str = "Status") -> list[dict]:
#     """Drop rows whose status indicates they're closed/inactive."""
#     CLOSED = {"closed", "inactive", "cancelled"}
#     return [r for r in rows if str(r.get(status_field) or "").strip().lower() not in CLOSED]


# def parse_sage_name(name: str) -> str:
#     """'LAST; FIRST' -> 'First Last' (Sage's name format is unusual)."""
#     if not name or ";" not in name:
#         return (name or "").strip()
#     last, first = name.split(";", 1)
#     return f"{first.strip()} {last.strip()}".strip()


# def join_address(row: dict) -> str:
#     """Combine address fields into a single line."""
#     parts = [row.get("Address_1"), row.get("City"), row.get("State"), row.get("Postal_Code")]
#     return ", ".join(p for p in parts if p)
