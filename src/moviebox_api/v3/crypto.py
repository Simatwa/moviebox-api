"""
Cryptographic utilities: request signing, HMAC-MD5, MD5, token generation.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
from urllib.parse import parse_qs, urlparse

from moviebox_api.v3.constants import (
    SECRET_KEY_ALT,
    SECRET_KEY_DEFAULT,
    SIGNATURE_BODY_MAX_BYTES,
)


def md5_hex(data: bytes) -> str:
    """Return lowercase hex MD5 of *data*."""
    return hashlib.md5(data).hexdigest()


def b64_decode(value: str) -> bytes:
    """Decode a standard-alphabet base64 string, adding padding if needed."""
    padding = (4 - len(value) % 4) % 4
    return base64.b64decode(value + "=" * padding)


def b64_encode(data: bytes) -> str:
    """Encode *data* to a standard base64 string (no newlines)."""
    return base64.b64encode(data).decode()


def generate_x_client_token(timestamp_ms: int | None = None) -> str:
    """
    token = "<ts>,<md5(reverse(<ts>))>"
    """
    ts = str(
        timestamp_ms if timestamp_ms is not None else int(time.time() * 1000)
    )
    reversed_ts = ts[::-1]
    hash_val = md5_hex(reversed_ts.encode())
    return f"{ts},{hash_val}"


def _sorted_query_string(url: str) -> str:
    """
    Rebuild the query string with keys in sorted order.
    Values are NOT percent-encoded.
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query, keep_blank_values=True)
    if not qs:
        return ""
    parts: list[str] = []
    for key in sorted(qs.keys()):
        for value in qs[key]:
            parts.append(f"{key}={value}")
    return "&".join(parts)


def build_canonical_string(
    method: str,
    accept: str | None,
    content_type: str | None,
    url: str,
    body: str | None,
    timestamp_ms: int,
) -> str:
    parsed = urlparse(url)
    path = parsed.path or ""
    query = _sorted_query_string(url)
    canonical_url = f"{path}?{query}" if query else path

    body_bytes: bytes | None = body.encode("utf-8") if body is not None else None
    if body_bytes is not None:
        truncated = body_bytes[:SIGNATURE_BODY_MAX_BYTES]
        body_hash = md5_hex(truncated)
        body_length = str(len(body_bytes))
    else:
        body_hash = ""
        body_length = ""

    return (
        f"{method.upper()}\n"
        f"{accept or ''}\n"
        f"{content_type or ''}\n"
        f"{body_length}\n"
        f"{timestamp_ms}\n"
        f"{body_hash}\n"
        f"{canonical_url}"
    )


def generate_x_tr_signature(
    method: str,
    accept: str | None,
    content_type: str | None,
    url: str,
    body: str | None = None,
    use_alt_key: bool = False,
    timestamp_ms: int | None = None,
) -> str:
    """
    Returns the ``x-tr-signature`` header value:
    ``"<ts>|2|<base64(hmac-md5(canonical, key))>"``
    """
    ts = timestamp_ms if timestamp_ms is not None else int(time.time() * 1000)
    canonical = build_canonical_string(
        method, accept, content_type, url, body, ts
    )
    secret_b64 = SECRET_KEY_ALT if use_alt_key else SECRET_KEY_DEFAULT
    secret_bytes = b64_decode(secret_b64)
    mac = hmac.new(secret_bytes, canonical.encode("utf-8"), hashlib.md5)
    sig_b64 = b64_encode(mac.digest())
    return f"{ts}|2|{sig_b64}"


def build_signed_headers(
    method: str,
    url: str,
    accept: str = "application/json",
    content_type: str = "application/json",
    body: str | None = None,
    include_play_mode: bool = False,
    auth_token: str | None = None,
    client_info: str = "",
    user_agent: str = "",
) -> dict[str, str]:
    """
    Assemble the full set of signed request headers.

    *auth_token* should be the runtime bearer token (may override the env-level
    token if a fresher one has been received from ``x-user`` response headers).
    """
    ts = int(time.time() * 1000)
    headers: dict[str, str] = {
        "User-Agent": user_agent,
        "Accept": accept,
        "Content-Type": content_type,
        "Connection": "keep-alive",
        "X-Client-Token": generate_x_client_token(ts),
        "x-tr-signature": generate_x_tr_signature(
            method, accept, content_type, url, body, False, ts
        ),
        "X-Client-Info": client_info,
        "X-Client-Status": "0",
    }
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    if include_play_mode:
        headers["X-Play-Mode"] = "2"
    return headers
