from __future__ import annotations

import re
from typing import Dict, List, Optional

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z\s.'-]{1,59}$")


def parse_float(value: str) -> Optional[float]:
    try:
        amount = float(value)
        if amount.is_integer():
            return float(int(amount))
        return amount
    except Exception:
        return None


def validate_login(email: str, password: str) -> List[str]:
    errors = []
    if not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    return errors


def validate_donation(form: Dict[str, str]) -> List[str]:
    errors: List[str] = []
    name = form.get("donor_name", "").strip()
    email = form.get("donor_email", "").strip()
    amount = form.get("amount", "").strip()
    purpose = form.get("purpose", "").strip()

    if not NAME_RE.match(name):
        errors.append("Enter a valid donor name.")
    if not EMAIL_RE.match(email):
        errors.append("Enter a valid donor email.")
    parsed_amount = parse_float(amount)
    if parsed_amount is None:
        errors.append("Donation amount must be numeric.")
    elif parsed_amount <= 0 or parsed_amount > 1_000_000:
        errors.append("Donation amount must be greater than 0 and within the allowed limit.")
    if len(purpose) < 3:
        errors.append("Purpose must be at least 3 characters.")
    if len(purpose) > 120:
        errors.append("Purpose must be 120 characters or fewer.")
    return errors

