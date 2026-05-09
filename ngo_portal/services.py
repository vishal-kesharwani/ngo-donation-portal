from __future__ import annotations

import datetime as dt
import sqlite3
from typing import Any, Dict, List, Tuple

from .config import LOGIN_WINDOW_MINUTES
from .database import connect_db
from .time_utils import iso_now, utcnow


def client_ip(environ: Dict[str, Any]) -> str:
    forwarded = environ.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return environ.get("REMOTE_ADDR", "127.0.0.1")


def log_event(event_type: str, details: str, environ: Dict[str, Any]) -> None:
    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO audit_events (event_type, details, ip_address, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (event_type, details, client_ip(environ), iso_now()),
        )
        conn.commit()


def login_window_start() -> str:
    return (utcnow() - dt.timedelta(minutes=LOGIN_WINDOW_MINUTES)).replace(microsecond=0).isoformat()


def failed_login_count(email: str, ip_address: str) -> int:
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM login_attempts
            WHERE email = ? AND ip_address = ? AND success = 0 AND created_at >= ?
            """,
            (email, ip_address, login_window_start()),
        ).fetchone()
        return int(row["count"]) if row else 0


def record_login_attempt(email: str, success: bool, environ: Dict[str, Any]) -> None:
    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO login_attempts (email, ip_address, success, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (email or "unknown", client_ip(environ), 1 if success else 0, iso_now()),
        )
        conn.commit()


def clear_failed_logins(email: str, ip_address: str) -> None:
    with connect_db() as conn:
        conn.execute(
            "DELETE FROM login_attempts WHERE email = ? AND ip_address = ? AND success = 0",
            (email, ip_address),
        )
        conn.commit()


def user_count() -> int:
    with connect_db() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        return int(row["count"]) if row else 0


def donation_totals() -> Tuple[int, float]:
    with connect_db() as conn:
        row = conn.execute("SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total FROM donations").fetchone()
        return int(row["count"]), float(row["total"])


def recent_donations(limit: int = 5) -> List[sqlite3.Row]:
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT d.*, u.name AS submitted_name, u.role AS submitted_role
            FROM donations d
            LEFT JOIN users u ON u.id = d.submitted_by
            ORDER BY d.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return list(rows)


def recent_events(limit: int = 8) -> List[sqlite3.Row]:
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return list(rows)


def recent_failed_login_total() -> int:
    with connect_db() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM login_attempts
            WHERE success = 0 AND created_at >= ?
            """,
            (login_window_start(),),
        ).fetchone()
        return int(row["count"]) if row else 0

