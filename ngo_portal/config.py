from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "ngo_portal.sqlite3"

SESSION_COOKIE = "ngo_session"
SECRET_KEY = os.environ.get("NGO_PORTAL_SECRET", "dev-secret-change-me").encode("utf-8")
SESSION_TTL_HOURS = 8

MAX_FAILED_LOGINS = 5
LOGIN_WINDOW_MINUTES = 15
SECURITY_CONTACT = "security-team@ngo.local"

