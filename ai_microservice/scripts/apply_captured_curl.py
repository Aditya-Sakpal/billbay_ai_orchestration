"""Apply captured.curl to .env and dashboard_api_endpoints.json."""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path
from urllib.parse import urlparse

from app.config import get_settings
from app.dashboard_auth import mask_cookie, phpsessid_from_cookie

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPTS_DIR.parent / ".env"
ENDPOINTS_FILE = SCRIPTS_DIR.parent / "data" / "dashboard_api_endpoints.json"

CURL_CANDIDATES = [
    ROOT / "captured.curl",
    SCRIPTS_DIR / "captured.curl",
]


def find_curl_file() -> Path | None:
    existing = [path for path in CURL_CANDIDATES if path.exists()]
    if not existing:
        return None
    return max(existing, key=lambda path: path.stat().st_mtime)


def parse_curl(curl_text: str) -> dict:
    cookie = ""
    cookie_match = re.search(r"""-b\s+['"]([^'"]+)['"]""", curl_text)
    if cookie_match:
        cookie = cookie_match.group(1)
    elif re.search(r"-b\s+(\S+)", curl_text):
        cookie = re.search(r"-b\s+(\S+)", curl_text).group(1).strip("'\"")

    normalized = curl_text.replace("\\\n", " ").replace("\r\n", "\n").replace("\n", " ")
    tokens = shlex.split(normalized, posix=True)
    url = ""
    method = "GET"
    headers: dict[str, str] = {}
    data_raw = ""

    i = 1
    while i < len(tokens):
        token = tokens[i]
        if token in ("-X", "--request") and i + 1 < len(tokens):
            method = tokens[i + 1].upper()
            i += 2
            continue
        if token in ("-H", "--header") and i + 1 < len(tokens):
            header = tokens[i + 1]
            if ":" in header:
                name, value = header.split(":", 1)
                headers[name.strip()] = value.strip()
            i += 2
            continue
        if token in ("-b", "--cookie") and i + 1 < len(tokens):
            if not cookie:
                cookie = tokens[i + 1].strip("'\"")
            i += 2
            continue
        if token in ("--data-raw", "--data", "-d") and i + 1 < len(tokens):
            data_raw = tokens[i + 1]
            method = "POST"
            i += 2
            continue
        if token.startswith("http"):
            url = token.strip("'\"")
            i += 1
            continue
        i += 1

    parsed = urlparse(url)
    payload = {}
    if data_raw:
        from urllib.parse import parse_qs

        if data_raw.strip().startswith("{"):
            payload = json.loads(data_raw)
        else:
            payload = {k: v[0] for k, v in parse_qs(data_raw).items()}

    return {
        "url": url,
        "path": parsed.path or "/dashboard.php",
        "method": method,
        "cookie": cookie or headers.get("Cookie", ""),
        "referer": headers.get("Referer", "https://csportal.billbay.co/dashboard.php"),
        "payload_template": payload,
        "content_type": headers.get("Content-Type", ""),
        "accept": headers.get("Accept", ""),
    }


def read_env_value(key: str) -> str:
    if not ENV_FILE.exists():
        return ""
    pattern = re.compile(rf"^{re.escape(key)}=(.*)$")
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return ""


def upsert_env(key: str, value: str) -> None:
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    pattern = re.compile(rf"^{re.escape(key)}=")
    new_line = f"{key}={value}"
    replaced = False
    out: list[str] = []
    for line in lines:
        if pattern.match(line):
            out.append(new_line)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(new_line)
    ENV_FILE.write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> int:
    curl_file = find_curl_file()
    if curl_file is None:
        print("Missing captured.curl. Checked:", file=sys.stderr)
        for candidate in CURL_CANDIDATES:
            print(f"  {candidate}", file=sys.stderr)
        return 1

    previous_cookie = read_env_value("DASHBOARD_SESSION_COOKIE")
    parsed = parse_curl(curl_file.read_text(encoding="utf-8"))
    base = f"{urlparse(parsed['url']).scheme}://{urlparse(parsed['url']).netloc}"

    upsert_env("DATA_SOURCE_MODE", "dashboard_api")
    upsert_env("DASHBOARD_BASE_URL", base)
    upsert_env("DASHBOARD_API_URL", parsed["path"])
    upsert_env("DASHBOARD_API_METHOD", parsed["method"])
    upsert_env("DASHBOARD_REFERER", parsed["referer"])
    if parsed["cookie"]:
        upsert_env("DASHBOARD_SESSION_COOKIE", parsed["cookie"])

    endpoints = json.loads(ENDPOINTS_FILE.read_text(encoding="utf-8"))
    page_mode = {
        "url": parsed["path"],
        "method": parsed["method"],
        "content_type": parsed["content_type"] or "text/html",
        "accept": parsed["accept"] or "text/html",
        "payload_template": parsed["payload_template"],
        "include_user_id": False,
        "response_mode": "html_table",
    }
    endpoints.setdefault("reports", {})["bbz_sales_perf"] = {
        **endpoints.get("reports", {}).get("bbz_sales_perf", {}),
        **page_mode,
    }
    endpoints["default"] = {**endpoints.get("default", {}), **page_mode}
    ENDPOINTS_FILE.write_text(json.dumps(endpoints, indent=2) + "\n", encoding="utf-8")

    get_settings.cache_clear()
    settings = get_settings()

    print("Updated .env and dashboard_api_endpoints.json")
    print(f"  source={curl_file}")
    print(f"  method={parsed['method']} url={parsed['path']}")
    print(f"  captured_cookie={mask_cookie(parsed['cookie'])}")
    print(f"  captured_phpsessid={mask_cookie(phpsessid_from_cookie(parsed['cookie']))}")
    print(f"  .env_cookie_now={mask_cookie(settings.dashboard_session_cookie)}")
    if previous_cookie and parsed["cookie"] and previous_cookie != parsed["cookie"]:
        print(f"  previous_env_cookie={mask_cookie(previous_cookie)} (replaced)")
        print(
            "\nWARNING: captured.curl PHPSESSID differs from what was in .env. "
            "If requests fail after this, export a fresh cURL from the browser while logged in."
        )
    if not parsed["cookie"]:
        print("\nWARNING: No PHPSESSID found in captured.curl — cookie not updated.")
    if parsed["method"] == "GET" and not parsed["payload_template"]:
        print("\nNOTE: captured request is a page load (GET dashboard.php), not XHR.")
        print("      HTML table parsing will be used until you capture a data API cURL.")
    print("\nNext request will reload the cookie from .env automatically (no uvicorn restart required).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
