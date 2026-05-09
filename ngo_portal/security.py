from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import secrets
from typing import Any, Dict, List, Optional, Tuple

from .config import SESSION_COOKIE, SESSION_TTL_HOURS, SECRET_KEY
from .time_utils import utcnow


def hash_password(password: str, salt_hex: Optional[str] = None) -> Tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return salt.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, expected_hex: str) -> bool:
    _, digest = hash_password(password, salt_hex)
    return hmac.compare_digest(digest, expected_hex)


def parse_cookies(environ: Dict[str, Any]) -> Dict[str, str]:
    raw = environ.get("HTTP_COOKIE", "")
    result: Dict[str, str] = {}
    for part in raw.split(";"):
        if "=" not in part:
            continue
        key, value = part.strip().split("=", 1)
        result[key] = value
    return result


def encode_session(payload: Dict[str, Any]) -> str:
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("ascii")
    sig = hmac.new(SECRET_KEY, body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def decode_session(token: str) -> Optional[Dict[str, Any]]:
    try:
        body, sig = token.split(".", 1)
        expected = hmac.new(SECRET_KEY, body.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body.encode("ascii")).decode("utf-8"))
        exp = dt.datetime.fromisoformat(payload["exp"])
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=dt.timezone.utc)
        if exp < utcnow():
            return None
        return payload
    except Exception:
        return None


def get_session(environ: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    token = parse_cookies(environ).get(SESSION_COOKIE)
    if not token:
        return None
    return decode_session(token)


def create_session(user: Any) -> str:
    payload = {
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "csrf": secrets.token_urlsafe(24),
        "exp": (utcnow() + dt.timedelta(hours=SESSION_TTL_HOURS)).isoformat(),
    }
    return encode_session(payload)


def session_cookie(token: str, environ: Dict[str, Any]) -> str:
    secure = "; Secure" if environ.get("wsgi.url_scheme") == "https" else ""
    max_age = SESSION_TTL_HOURS * 60 * 60
    return f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}{secure}"


def clear_session_cookie() -> str:
    return f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"


def security_headers() -> List[Tuple[str, str]]:
    return [
        ("Content-Security-Policy", "default-src 'self'; style-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"),
        ("X-Frame-Options", "DENY"),
        ("X-Content-Type-Options", "nosniff"),
        ("Referrer-Policy", "same-origin"),
        ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
        ("Cache-Control", "no-store"),
    ]

