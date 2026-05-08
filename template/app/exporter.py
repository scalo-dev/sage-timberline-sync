"""
Generic exporter skeleton.

Pull -> Enrich -> Write. Each phase is its own function so you can
swap any of them out without touching the others.

Run directly:
  C:\\Python311-32\\python.exe -m app.exporter

Import in your own code:
  from app.exporter import run_export
  result = run_export()
"""
from __future__ import annotations

import csv
import datetime as dt
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from . import config
from . import enrichment
from . import sage_query

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
@dataclass
class ExportResult:
    started_at: dt.datetime
    finished_at: Optional[dt.datetime] = None
    success: bool = False
    error: Optional[str] = None
    row_count: int = 0
    output_files: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Pull (override if you need joins or multiple queries)
# ---------------------------------------------------------------------------
def pull() -> list[dict]:
    """Read raw rows from Sage."""
    rows = sage_query.select()
    log.info("Pulled %d rows from %s", len(rows), config.SAGE_TABLE)
    return rows


# ---------------------------------------------------------------------------
# Enrich (delegate to enrichment.py)
# ---------------------------------------------------------------------------
def enrich(rows: list[dict]) -> list[dict]:
    out = enrichment.enrich_all(rows)
    log.info("Enriched %d rows", len(out))
    return out


# ---------------------------------------------------------------------------
# Write (CSV by default - swap for SQLite, Postgres, webhook, etc.)
# ---------------------------------------------------------------------------
def write_csv(
    rows: Iterable[dict],
    path: Path,
    columns: Optional[list[str]] = None,
) -> int:
    """Write rows to a UTF-8 CSV with a BOM (so Excel opens it cleanly)."""
    rows = list(rows)
    if not rows:
        log.warning("No rows to write to %s", path)
        return 0
    fieldnames = columns or list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline='' avoids double line endings on Windows.
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    log.info("Wrote %d rows to %s", len(rows), path)
    return len(rows)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
def run_export() -> ExportResult:
    result = ExportResult(started_at=dt.datetime.now())
    try:
        raw = pull()
        enriched = enrich(raw)

        out_path = config.OUTPUT_DIR / f"{config.SAGE_TABLE.lower()}.csv"
        n = write_csv(enriched, out_path)
        result.row_count = n
        result.output_files.append(str(out_path))
        result.success = True
    except Exception as exc:
        log.exception("Export failed")
        result.success = False
        result.error = str(exc)
    finally:
        result.finished_at = dt.datetime.now()
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _setup_logging() -> None:
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = config.LOGS_DIR / "exporter.log"
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(fh)
    root.addHandler(sh)


if __name__ == "__main__":
    _setup_logging()
    res = run_export()
    if res.success:
        elapsed = (res.finished_at - res.started_at).total_seconds()
        print(f"\nOK - wrote {res.row_count} rows in {elapsed:.1f}s")
        for f in res.output_files:
            print(f"  {f}")
        raise SystemExit(0)
    else:
        print(f"\nFAILED: {res.error}")
        raise SystemExit(1)
