from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs

from .config import LOGIN_WINDOW_MINUTES, MAX_FAILED_LOGINS
from .database import connect_db, ensure_storage, get_user_by_email
from .security import clear_session_cookie, create_session, get_session, security_headers, session_cookie, verify_password
from .services import (
    clear_failed_logins,
    client_ip,
    donation_totals,
    failed_login_count,
    log_event,
    recent_events,
    record_login_attempt,
)
from .time_utils import iso_now
from .validators import validate_donation, validate_login
from .views import access_denied, dashboard_page, donate_page, home_page, login_page, page_shell


def read_form(environ: Dict[str, Any]) -> Dict[str, str]:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length).decode("utf-8")
    parsed = parse_qs(body, keep_blank_values=True)
    return {key: values[0] if values else "" for key, values in parsed.items()}


def response_html(start_response, html_text: str, status: str = "200 OK", headers: Optional[List[Tuple[str, str]]] = None):
    final_headers = [("Content-Type", "text/html; charset=utf-8")]
    final_headers.extend(security_headers())
    if headers:
        final_headers.extend(headers)
    start_response(status, final_headers)
    return [html_text.encode("utf-8")]


def response_json(start_response, payload: Dict[str, Any], status: str = "200 OK"):
    start_response(status, [("Content-Type", "application/json; charset=utf-8"), *security_headers()])
    return [json.dumps(payload, indent=2).encode("utf-8")]


def response_static(start_response, file_path: Path):
    if not file_path.exists():
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8"), *security_headers()])
        return [b"Static file not found"]
    start_response("200 OK", [("Content-Type", "text/css; charset=utf-8"), *security_headers()])
    return [file_path.read_bytes()]


def redirect(start_response, location: str, cookie: Optional[str] = None):
    headers = [("Location", location)]
    if cookie:
        headers.append(("Set-Cookie", cookie))
    start_response("302 Found", headers)
    return [b"Redirecting..."]


def dashboard_response(start_response, session: Dict[str, Any], is_admin: bool):
    with connect_db() as conn:
        if is_admin:
            donations = conn.execute(
                """
                SELECT d.*, u.name AS submitted_name
                FROM donations d
                LEFT JOIN users u ON u.id = d.submitted_by
                ORDER BY d.id DESC
                LIMIT 12
                """
            ).fetchall()
        else:
            donations = conn.execute(
                """
                SELECT d.*
                FROM donations d
                WHERE d.submitted_by = ?
                ORDER BY d.id DESC
                LIMIT 12
                """,
                (session["user_id"],),
            ).fetchall()
    return response_html(start_response, dashboard_page(session, list(donations), is_admin=is_admin))


def app(environ: Dict[str, Any], start_response):
    ensure_storage()
    method = environ["REQUEST_METHOD"].upper()
    path = environ.get("PATH_INFO", "/")
    session = get_session(environ)

    if path == "/static/styles.css":
        return response_static(start_response, Path(__file__).resolve().parent / "static" / "styles.css")

    if path == "/":
        return response_html(start_response, home_page(session))

    if path == "/login" and method == "GET":
        return response_html(start_response, login_page(session))

    if path == "/login" and method == "POST":
        form = read_form(environ)
        email = form.get("email", "").strip().lower()
        password = form.get("password", "")
        ip_address = client_ip(environ)

        if failed_login_count(email or "unknown", ip_address) >= MAX_FAILED_LOGINS:
            log_event("AUTH_RATE_LIMITED", f"Too many failed login attempts for {email or 'unknown'}", environ)
            return response_html(
                start_response,
                login_page(session, error=f"Too many failed attempts. Try again after {LOGIN_WINDOW_MINUTES} minutes."),
                status="429 Too Many Requests",
            )

        errors = validate_login(email, password)
        if errors:
            record_login_attempt(email or "unknown", False, environ)
            log_event("AUTH_LOGIN_FAILURE", f"Validation rejected login for {email or 'unknown'}", environ)
            return response_html(start_response, login_page(session, error=" ".join(errors)))

        user = get_user_by_email(email)
        if not user or not verify_password(password, user["password_salt"], user["password_hash"]):
            record_login_attempt(email, False, environ)
            log_event("AUTH_LOGIN_FAILURE", f"Invalid credentials for {email}", environ)
            return response_html(start_response, login_page(session, error="Invalid email or password."))

        record_login_attempt(email, True, environ)
        clear_failed_logins(email, ip_address)
        token = create_session(user)
        log_event("AUTH_LOGIN_SUCCESS", f"{user['email']} signed in as {user['role']}", environ)
        target = "/admin/dashboard" if user["role"] == "admin" else "/dashboard"
        return redirect(start_response, target, cookie=session_cookie(token, environ))

    if path == "/donate" and method == "GET":
        if not session:
            return response_html(start_response, donate_page(session, error="Please login before submitting a donation."))
        return response_html(start_response, donate_page(session))

    if path == "/donate" and method == "POST":
        if not session:
            return response_html(start_response, donate_page(session, error="Authentication required."), status="401 Unauthorized")
        form = read_form(environ)
        csrf = form.get("csrf", "")
        if not csrf or csrf != session.get("csrf"):
            log_event("CSRF_BLOCKED", f"CSRF mismatch for user_id={session['user_id']}", environ)
            return response_html(start_response, donate_page(session, error="CSRF validation failed."), status="400 Bad Request")

        errors = validate_donation(form)
        if errors:
            log_event("DONATION_REJECTED", f"Rejected donation payload from {session['email']}: {errors[0]}", environ)
            return response_html(start_response, donate_page(session, error=" ".join(errors)))

        amount = float(form["amount"])
        donor_name = form["donor_name"].strip()
        donor_email = form["donor_email"].strip().lower()
        purpose = form["purpose"].strip()
        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO donations (donor_name, donor_email, amount, purpose, status, submitted_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (donor_name, donor_email, amount, purpose, "Approved", session["user_id"], iso_now()),
            )
            conn.commit()
        log_event("DONATION_ACCEPTED", f"Donation stored for {donor_email} amount={amount}", environ)
        return response_html(start_response, donate_page(session, notice="Donation submitted successfully."))

    if path == "/dashboard" and method == "GET":
        if not session:
            return response_html(start_response, access_denied(session, "Login is required."), status="401 Unauthorized")
        if session["role"] not in {"donor", "admin"}:
            return response_html(start_response, access_denied(session), status="403 Forbidden")
        return dashboard_response(start_response, session, is_admin=False)

    if path == "/admin/dashboard" and method == "GET":
        if not session:
            log_event("ACCESS_DENIED", "Anonymous attempt to access admin dashboard", environ)
            return response_html(start_response, access_denied(session, "Admin login required."), status="401 Unauthorized")
        if session["role"] != "admin":
            log_event("ACCESS_DENIED", f"User {session['email']} blocked from admin dashboard", environ)
            return response_html(start_response, access_denied(session, "Admin role required."), status="403 Forbidden")
        return dashboard_response(start_response, session, is_admin=True)

    if path == "/api/summary" and method == "GET":
        if not session:
            return response_json(start_response, {"error": "Authentication required"}, status="401 Unauthorized")
        if session["role"] != "admin":
            return response_json(start_response, {"error": "Admin role required"}, status="403 Forbidden")
        count, total = donation_totals()
        return response_json(start_response, {"donations": count, "total_amount": total, "recent_events": [dict(row) for row in recent_events(5)]})

    if path == "/logout" and method == "POST":
        if session:
            form = read_form(environ)
            if form.get("csrf") != session.get("csrf"):
                log_event("CSRF_BLOCKED", f"CSRF mismatch during logout for user_id={session['user_id']}", environ)
                return response_html(start_response, access_denied(session, "CSRF validation failed."), status="400 Bad Request")
            log_event("AUTH_LOGOUT", f"{session['email']} signed out", environ)
        return redirect(start_response, "/", cookie=clear_session_cookie())

    return response_html(
        start_response,
        page_shell("Not found", session, '<h2>404 - Page not found</h2><p class="muted">The requested route does not exist.</p>'),
        status="404 Not Found",
    )
