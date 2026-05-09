from __future__ import annotations

from typing import List, Tuple

from .config import LOGIN_WINDOW_MINUTES, MAX_FAILED_LOGINS


def control_rows() -> List[Tuple[str, str, str]]:
    return [
        ("Authentication", "PBKDF2 password hashing, signed sessions, session expiry", "Implemented"),
        ("Authorization", "Donor/admin RBAC on dashboards and API routes", "Implemented"),
        ("Input validation", "Strict server-side validation and parameterized SQLite queries", "Implemented"),
        ("CSRF defense", "Session-bound CSRF token on state-changing requests", "Implemented"),
        ("Monitoring", "Audit events for login, logout, blocked access, CSRF, and donations", "Implemented"),
        ("Brute-force control", f"{MAX_FAILED_LOGINS} failed logins blocked per {LOGIN_WINDOW_MINUTES} minutes", "Implemented"),
        ("Browser hardening", "CSP, frame denial, no-sniff, referrer, permissions, and no-store headers", "Implemented"),
        ("Patch management", "Use pinned dependencies in production and review patches monthly", "Planned"),
        ("Firewall rules", "Expose only HTTPS reverse proxy; keep database private", "Production design"),
    ]


def risk_rows() -> List[Tuple[str, str, str, str]]:
    return [
        ("SQL injection", "High", "Parameterized queries and input validation", "Low"),
        ("Broken access control", "High", "RBAC checks on dashboard and API routes", "Low"),
        ("CSRF", "Medium", "Hidden session token verified server-side", "Low"),
        ("Brute-force login", "Medium", "Sliding-window failed login throttling", "Medium"),
        ("Session theft", "High", "HttpOnly SameSite cookies; use HTTPS Secure flag in deployment", "Medium"),
        ("Sensitive data exposure", "High", "Least-privilege admin views and no-store headers", "Medium"),
    ]

