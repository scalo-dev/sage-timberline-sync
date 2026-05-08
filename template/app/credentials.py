"""
Credential loader.

Reads UID/PWD from instance/sage_credentials.ini. The file format:

    UID=yourSageUsername
    PWD=yourSagePassword

This file MUST be in .gitignore. Never commit credentials.
"""
from __future__ import annotations

from . import config


def load_credentials() -> tuple[str, str]:
    """Return (UID, PWD) read from CREDENTIALS_FILE. Raises if missing."""
    path = config.CREDENTIALS_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"Sage credentials file not found at {path}.\n"
            "Create it with two lines:\n"
            "  UID=yourusername\n"
            "  PWD=yourpassword"
        )
    uid = pwd = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("UID="):
            uid = line[4:].strip()
        elif line.startswith("PWD="):
            pwd = line[4:].strip()
    if not uid or not pwd:
        raise ValueError(f"Credentials file {path} is missing UID or PWD")
    return uid, pwd
