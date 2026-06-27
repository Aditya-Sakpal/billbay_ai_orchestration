"""Probe csportal dashboard HTML for tables and AJAX endpoints."""

from __future__ import annotations

import re
import sys

import httpx

COOKIE = sys.argv[1] if len(sys.argv) > 1 else ""


def main() -> int:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://csportal.billbay.co/dashboard.php",
    }
    if COOKIE:
        headers["Cookie"] = COOKIE

    r = httpx.get(
        "https://csportal.billbay.co/dashboard.php",
        headers=headers,
        follow_redirects=True,
        timeout=30,
    )
    print("status", r.status_code)
    print("url", r.url)
    print("len", len(r.text))
    text = r.text

    endpoints = set()
    for m in re.finditer(r"""['"]([^'"]+\.php[^'"]*)['"]""", text, re.I):
        val = m.group(1)
        if any(k in val.lower() for k in ("ajax", "report", "data", "load", "fetch", "api")):
            endpoints.add(val)
    print("\nPossible endpoints:")
    for e in sorted(endpoints)[:30]:
        print(" ", e)

    print("\ntables", text.lower().count("<table"))
    print("salesperson mentions", text.lower().count("salesperson"))

    title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    if title:
        print("title:", re.sub(r"\s+", " ", title.group(1)).strip()[:120])

    if "login" in str(r.url).lower() or re.search(r"type=[\"']password[\"']", text, re.I):
        print("\nNOTE: response looks like a login page — cookie may be expired")

    # sample first table headers
    thead = re.search(r"<thead[^>]*>(.*?)</thead>", text, re.I | re.S)
    if thead:
        ths = re.findall(r"<th[^>]*>(.*?)</th>", thead.group(1), re.I | re.S)
        ths = [re.sub(r"<[^>]+>", "", t).strip() for t in ths[:12]]
        print("\nfirst table headers:", ths)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
