from __future__ import annotations

import sqlite3
from typing import Optional

from .config import DATA_DIR, DB_PATH
from .security import hash_password
from .time_utils import iso_now


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('donor', 'admin')),
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_name TEXT NOT NULL,
                donor_email TEXT NOT NULL,
                amount REAL NOT NULL,
                purpose TEXT NOT NULL,
                status TEXT NOT NULL,
                submitted_by INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(submitted_by) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                details TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                success INTEGER NOT NULL CHECK(success IN (0, 1)),
                created_at TEXT NOT NULL
            )
            """
        )
        seed_users(conn)
        conn.commit()


def seed_users(conn: sqlite3.Connection) -> None:
    rows = conn.execute("SELECT COUNT(*) FROM users").fetchone()
    if rows and rows[0]:
        return

    demo_users = [
        ("Vidya Bingi", "donor@ngo.local", "Donor@1234", "donor"),
        ("Vishal Kesharwani", "admin@ngo.local", "Admin@1234", "admin"),
    ]
    for name, email, password, role in demo_users:
        salt, digest = hash_password(password)
        conn.execute(
            """
            INSERT INTO users (name, email, password_salt, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, email, salt, digest, role, iso_now()),
        )

    conn.execute(
        """
        INSERT INTO donations (donor_name, donor_email, amount, purpose, status, submitted_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("Vidya Bingi", "donor@ngo.local", 1500.0, "School supplies", "Approved", 1, iso_now()),
    )
    conn.execute(
        """
        INSERT INTO audit_events (event_type, details, ip_address, created_at)
        VALUES (?, ?, ?, ?)
        """,
        ("SYSTEM_SEED", "Seeded default demo accounts and sample donation", "127.0.0.1", iso_now()),
    )


def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    with connect_db() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    with connect_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

