"""
Long-running entrypoint for NSSM.

Runs app.exporter.run_export() in a loop with a configurable sleep
between iterations. Catches and logs failures so the service stays up
even if a single run errors out.

For more elaborate services (Flask UI + APScheduler, multiple jobs,
etc.), replace the body of main() with whatever you need.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

from app import config
from app.exporter import run_export


# Sleep this long between exports. Override with the env var
# EXPORT_INTERVAL_SECONDS if you want different intervals per environment.
DEFAULT_INTERVAL_SECONDS = 4 * 60 * 60  # 4 hours


def _setup_logging() -> None:
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = RotatingFileHandler(
        config.LOGS_DIR / "service.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(fh)
    root.addHandler(sh)


def main() -> int:
    _setup_logging()
    log = logging.getLogger("run_service")

    interval = int(os.environ.get("EXPORT_INTERVAL_SECONDS", DEFAULT_INTERVAL_SECONDS))
    log.info("Starting service. Interval: %d seconds", interval)

    while True:
        try:
            res = run_export()
            if res.success:
                log.info("Export OK: %d rows", res.row_count)
            else:
                log.error("Export FAILED: %s", res.error)
        except Exception:
            log.exception("Unhandled error during export")
        log.info("Sleeping %d seconds until next run...", interval)
        time.sleep(interval)


if __name__ == "__main__":
    sys.exit(main() or 0)
