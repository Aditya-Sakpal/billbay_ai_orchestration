"""
Verify dashboard session cookie and live connectivity.

Usage:
  cd ai_microservice
  python -m scripts.verify_dashboard_session
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

from app.config import get_settings
from app.dashboard_auth import mask_cookie, mask_headers, phpsessid_from_cookie, refresh_dashboard_settings
from app.repositories.dashboard_api_repository import DashboardApiError, DashboardApiRepository

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = Path(__file__).resolve().parent


def _curl_sources() -> list[Path]:
    return [ROOT / "captured.curl", SCRIPTS_DIR / "captured.curl"]


async def probe_dashboard(settings) -> tuple[int, str, str]:
    url = settings.dashboard_base_url.rstrip("/") + settings.dashboard_api_url
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": settings.dashboard_referer,
        "Cookie": settings.dashboard_session_cookie,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
    }
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
    return response.status_code, str(response.url), response.text[:500]


async def main() -> int:
    settings = refresh_dashboard_settings()
    cookie = settings.dashboard_session_cookie

    print("=== Dashboard session verification ===\n")
    print(f"DATA_SOURCE_MODE={settings.data_source_mode}")
    print(f"DASHBOARD_BASE_URL={settings.dashboard_base_url}")
    print(f"DASHBOARD_API_URL={settings.dashboard_api_url}")
    print(f"DASHBOARD_SESSION_COOKIE (masked)={mask_cookie(cookie)}")
    print(f"PHPSESSID (masked)={mask_cookie(phpsessid_from_cookie(cookie))}")

    print("\n--- captured.curl sources ---")
    for path in _curl_sources():
        if not path.exists():
            print(f"  {path}: (missing)")
            continue
        text = path.read_text(encoding="utf-8")
        import re

        match = re.search(r"PHPSESSID=([^'\s;]+)", text)
        sess = match.group(1) if match else ""
        print(f"  {path}: PHPSESSID={mask_cookie(sess)} mtime={path.stat().st_mtime:.0f}")

    env_sess = phpsessid_from_cookie(cookie)
    curl_sessids = []
    for path in _curl_sources():
        if path.exists():
            import re

            match = re.search(r"PHPSESSID=([^'\s;]+)", path.read_text(encoding="utf-8"))
            if match:
                curl_sessids.append((path.name, match.group(1)))
    if curl_sessids and env_sess:
        newest_name, newest_sess = max(
            curl_sessids,
            key=lambda item: next(
                p.stat().st_mtime
                for p in _curl_sources()
                if p.name == item[0] and p.exists()
            ),
        )
        if env_sess != newest_sess:
            print(
                f"\nNOTE: .env PHPSESSID ({mask_cookie(env_sess)}) differs from "
                f"newest captured.curl ({newest_name}, {mask_cookie(newest_sess)}). "
                "captured.curl may be stale — export a fresh cURL from the browser "
                "while logged in, then run: python -m scripts.apply_captured_curl"
            )

    if not cookie:
        print("\nERROR: DASHBOARD_SESSION_COOKIE is empty in .env")
        return 1

    print("\n--- direct HTTP probe ---")
    status, final_url, preview = await probe_dashboard(settings)
    print(f"  request_url={settings.dashboard_base_url.rstrip('/')}{settings.dashboard_api_url}")
    print(f"  headers={mask_headers({'Cookie': cookie, 'Referer': settings.dashboard_referer})}")
    print(f"  status={status}")
    print(f"  final_url={final_url}")
    print(f"  body_preview={preview!r}")

    if "st=ses" in final_url.lower() or (
        "/index.php" in final_url.lower() and "dashboard.php" not in final_url.lower()
    ):
        print("\nRESULT: Session expired (redirected to login)")
        return 1

    print("\n--- repository execute_report probe ---")
    repo = DashboardApiRepository()
    try:
        rows = await repo.execute_report(
            report_id=1,
            sql_table_name="bbz_sales_perf",
            report_name="verify",
            bound_filters={},
            user_id=42,
            access_level=50,
        )
    except DashboardApiError as exc:
        print(f"RESULT: {exc}")
        return 1

    print(f"RESULT: OK — {len(rows)} salesperson row(s) returned")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
