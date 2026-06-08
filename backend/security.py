"""Authentication & security utilities.

Implements password hashing (PBKDF2-HMAC-SHA256) and stateless HS256
JSON Web Tokens using only the Python standard library, so the platform
runs with zero extra dependencies while remaining production-shaped.

Developed by Jillani SofTech.
"""
import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional

from backend.config import settings


# --------------------------------------------------------------------------- #
# Password hashing
# --------------------------------------------------------------------------- #
def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120_000)
    return f"{salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, _ = stored.split("$", 1)
        return hmac.compare_digest(stored, hash_password(password, bytes.fromhex(salt_hex)))
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# JWT (HS256) - standard library implementation
# --------------------------------------------------------------------------- #
def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def create_access_token(subject: str, name: str = "", role: str = "admin") -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": subject,
        "name": name,
        "role": role,
        "iat": now,
        "exp": now + settings.TOKEN_EXPIRE_MINUTES * 60,
        "iss": "FinServe-AI-Copilot",
    }
    seg = f"{_b64url(json.dumps(header).encode())}.{_b64url(json.dumps(payload).encode())}"
    sig = hmac.new(settings.SECRET_KEY.encode(), seg.encode(), hashlib.sha256).digest()
    return f"{seg}.{_b64url(sig)}"


def decode_access_token(token: str) -> Optional[dict]:
    try:
        seg, sig_b64 = token.rsplit(".", 1)
        expected = hmac.new(settings.SECRET_KEY.encode(), seg.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url(expected), sig_b64):
            return None
        payload = json.loads(_b64url_decode(seg.split(".", 1)[1]))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None
