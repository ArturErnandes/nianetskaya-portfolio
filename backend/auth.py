import base64
import hashlib
import hmac
import json
import time
from dataclasses import asdict
from secrets import compare_digest
from typing import Optional

from fastapi import Request, Response

from .classes import AdminSessionData
from .config import AdminConfig

ADMIN_SESSION_COOKIE = "admin_session"
ADMIN_SESSION_MAX_AGE = 60 * 60 * 12


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64_decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def _signing_key() -> bytes:
    return hashlib.sha256(f"admin-cookie:{AdminConfig.password_hash}".encode()).digest()


def verify_admin_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_raw, salt_raw, hash_raw = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_raw)
        salt = _b64_decode(salt_raw)
        expected_hash = _b64_decode(hash_raw)
    except (ValueError, TypeError):
        return False

    candidate_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return compare_digest(candidate_hash, expected_hash)


def _build_signed_cookie_payload(session: AdminSessionData) -> str:
    payload = _b64_encode(json.dumps(asdict(session), separators=(",", ":")).encode())
    signature = _b64_encode(hmac.new(_signing_key(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"


def create_admin_session_cookie() -> str:
    now = int(time.time())
    session = AdminSessionData(role="admin", iat=now, exp=now + ADMIN_SESSION_MAX_AGE)
    return _build_signed_cookie_payload(session)


def read_admin_session_cookie(cookie_value: Optional[str]) -> Optional[AdminSessionData]:
    if not cookie_value or "." not in cookie_value:
        return None

    payload_raw, signature_raw = cookie_value.split(".", 1)
    expected_signature = _b64_encode(
        hmac.new(_signing_key(), payload_raw.encode(), hashlib.sha256).digest()
    )
    if not compare_digest(signature_raw, expected_signature):
        return None

    try:
        payload = json.loads(_b64_decode(payload_raw))
        session = AdminSessionData(
            role=payload["role"],
            iat=int(payload["iat"]),
            exp=int(payload["exp"]),
        )
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return None

    if session.role != "admin" or session.exp <= int(time.time()):
        return None

    return session


def set_admin_session_cookie(response: Response):
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE,
        value=create_admin_session_cookie(),
        max_age=ADMIN_SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=True,
        path="/",
    )


def clear_admin_session_cookie(response: Response):
    response.delete_cookie(
        key=ADMIN_SESSION_COOKIE,
        httponly=True,
        samesite="lax",
        secure=True,
        path="/",
    )


def has_admin_access(request: Request) -> bool:
    cookie_value = request.cookies.get(ADMIN_SESSION_COOKIE)
    return read_admin_session_cookie(cookie_value) is not None
