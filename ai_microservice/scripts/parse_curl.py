"""
Parse a Chrome DevTools "Copy as cURL" string into .env hints and endpoint JSON.

Usage:
  python -m scripts.parse_curl --curl-file captured.curl
  python -m scripts.parse_curl --curl "curl 'https://...' -H 'Cookie: ...' --data-raw 'action=...'"
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def parse_curl(curl_text: str) -> dict:
    tokens = shlex.split(curl_text.replace("\\\n", " ").replace("\n", " "))
    if not tokens or tokens[0] != "curl":
        raise ValueError("Input must start with 'curl'")

    url = ""
    method = "POST"
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
        if token in ("--data-raw", "--data", "-d") and i + 1 < len(tokens):
            data_raw = tokens[i + 1]
            i += 2
            continue
        if token.startswith("http"):
            url = token.strip("'\"")
            i += 1
            continue
        i += 1

    payload: dict[str, str] = {}
    content_type = headers.get("Content-Type", "")
    if data_raw:
        if "application/json" in content_type or data_raw.strip().startswith("{"):
            payload = json.loads(data_raw)
        else:
            payload = {k: v[0] for k, v in parse_qs(data_raw).items()}

    parsed_url = urlparse(url)
    return {
        "url": parsed_url.path or url,
        "full_url": url,
        "method": method,
        "headers": {k: v for k, v in headers.items() if k.lower() != "cookie"},
        "cookie": headers.get("Cookie", ""),
        "payload_template": payload,
        "content_type": headers.get("Content-Type", "application/x-www-form-urlencoded"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curl", help="cURL string")
    parser.add_argument("--curl-file", help="Path to file containing cURL")
    parser.add_argument("--table", default="bbz_sales_perf")
    args = parser.parse_args()

    if args.curl_file:
        curl_text = Path(args.curl_file).read_text(encoding="utf-8")
    elif args.curl:
        curl_text = args.curl
    else:
        print("Provide --curl or --curl-file", file=sys.stderr)
        return 1

    parsed = parse_curl(curl_text)

    print("=== Add to ai_microservice/.env ===\n")
    print("DATA_SOURCE_MODE=dashboard_api")
    print(f"DASHBOARD_BASE_URL={urlparse(parsed['full_url']).scheme}://{urlparse(parsed['full_url']).netloc}")
    print(f"DASHBOARD_API_URL={parsed['url']}")
    print(f"DASHBOARD_API_METHOD={parsed['method']}")
    if parsed["cookie"]:
        redacted = re.sub(r"(PHPSESSID|session)[^;]*", r"\1=REDACTED", parsed["cookie"], flags=re.I)
        print(f"DASHBOARD_SESSION_COOKIE={redacted}")
    print()

    endpoint = {
        "url": parsed["url"],
        "method": parsed["method"],
        "content_type": parsed["content_type"],
        "payload_template": parsed["payload_template"],
        "headers": parsed["headers"],
        "response_rows_path": "rows",
    }
    print(f"=== Merge into data/dashboard_api_endpoints.json → reports.{args.table} ===\n")
    print(json.dumps(endpoint, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
