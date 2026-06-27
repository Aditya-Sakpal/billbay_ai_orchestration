"""
Check Anthropic credentials and optionally fetch org API key metadata.

Chat completions require ANTHROPIC_API_KEY (sk-ant-...) OR ANTHROPIC_OAUTH_TOKEN.

The organizations endpoint below lists API key metadata — it does NOT return
the secret key value. Create a new key at https://console.anthropic.com/settings/keys

Usage:
  # Standard API key (recommended for this project)
  set ANTHROPIC_API_KEY=sk-ant-api03-...
  python scripts/anthropic_auth_check.py

  # Org admin lookup (metadata only)
  set ANTHROPIC_OAUTH_TOKEN=...
  set ANTHROPIC_API_KEY_ID=...
  python scripts/anthropic_auth_check.py --fetch-key-info
"""

from __future__ import annotations

import argparse
import os
import sys

import httpx


def _chat_test_api_key(api_key: str) -> None:
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5",
            "max_tokens": 16,
            "messages": [{"role": "user", "content": "Reply with OK only."}],
        },
        timeout=30.0,
    )
    print(f"Messages API (x-api-key): HTTP {response.status_code}")
    if response.status_code != 200:
        print(response.text[:500])
        return
    print("Chat API key works.")


def _chat_test_oauth(oauth_token: str) -> None:
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Authorization": f"Bearer {oauth_token}",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5",
            "max_tokens": 16,
            "messages": [{"role": "user", "content": "Reply with OK only."}],
        },
        timeout=30.0,
    )
    print(f"Messages API (Bearer OAuth): HTTP {response.status_code}")
    if response.status_code != 200:
        print(response.text[:500])
        return
    print("OAuth token works for chat.")


def _fetch_api_key_info(oauth_token: str, api_key_id: str) -> None:
    url = f"https://api.anthropic.com/v1/organizations/api_keys/{api_key_id}"
    response = httpx.get(
        url,
        headers={
            "Authorization": f"Bearer {oauth_token}",
            "anthropic-version": "2023-06-01",
        },
        timeout=30.0,
    )
    print(f"Organizations API: HTTP {response.status_code}")
    print(response.text[:2000])


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Anthropic credentials")
    parser.add_argument(
        "--fetch-key-info",
        action="store_true",
        help="Call GET /v1/organizations/api_keys/{id} (metadata only)",
    )
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    oauth_token = os.getenv("ANTHROPIC_OAUTH_TOKEN", "")
    api_key_id = os.getenv("ANTHROPIC_API_KEY_ID", "")

    if args.fetch_key_info:
        if not oauth_token or not api_key_id:
            print(
                "Set ANTHROPIC_OAUTH_TOKEN and ANTHROPIC_API_KEY_ID for --fetch-key-info",
                file=sys.stderr,
            )
            return 1
        _fetch_api_key_info(oauth_token, api_key_id)
        return 0

    if api_key and api_key not in ("your-anthropic-api-key", ""):
        _chat_test_api_key(api_key)
        return 0

    if oauth_token:
        _chat_test_oauth(oauth_token)
        return 0

    print(
        "No credentials found. Set ANTHROPIC_API_KEY (sk-ant-...) in ai_microservice/.env",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
