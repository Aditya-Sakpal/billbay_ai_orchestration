"""Dashboard session cookie helpers (auth only)."""

from __future__ import annotations

import re

from app.config import get_settings


def mask_cookie(cookie: str, visible: int = 10) -> str:
    if not cookie:
        return "(empty)"
    if len(cookie) <= visible:
        return cookie[:3] + "***"
    return cookie[:visible] + "***"


def mask_headers(headers: dict[str, str]) -> dict[str, str]:
    masked: dict[str, str] = {}
    for key, value in headers.items():
        if key.lower() == "cookie":
            masked[key] = mask_cookie(value)
        else:
            masked[key] = value
    return masked


def refresh_dashboard_settings():
    """Reload .env so DASHBOARD_SESSION_COOKIE changes apply without full restart."""
    get_settings.cache_clear()
    return get_settings()


def phpsessid_from_cookie(cookie: str) -> str:
    match = re.search(r"PHPSESSID=([^;\s]+)", cookie, re.I)
    return match.group(1) if match else ""
