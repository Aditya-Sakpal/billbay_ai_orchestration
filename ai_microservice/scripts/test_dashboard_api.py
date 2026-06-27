"""
Test live dashboard API connection (Option A).

Usage:
  cd ai_microservice
  python -m scripts.test_dashboard_api
  python -m scripts.test_dashboard_api --table bbz_sales_perf
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from app.config import get_settings
from app.dashboard_auth import mask_cookie, phpsessid_from_cookie, refresh_dashboard_settings
from app.repositories.dashboard_api_repository import DashboardApiError, DashboardApiRepository


async def main() -> int:
    parser = argparse.ArgumentParser(description="Test Cornerstone dashboard API")
    parser.add_argument(
        "--table",
        default="bbz_sales_perf",
        help="sql_table_name from catalog (default: bbz_sales_perf)",
    )
    parser.add_argument("--report-id", type=int, default=1)
    parser.add_argument("--user-id", type=int, default=42)
    args = parser.parse_args()

    get_settings.cache_clear()
    settings = refresh_dashboard_settings()
    print(f"data_source_mode would be: {settings.data_source_mode}")
    print(f"dashboard_base_url: {settings.dashboard_base_url}")
    print(f"cookie (masked): {mask_cookie(settings.dashboard_session_cookie)}")
    print(f"PHPSESSID (masked): {mask_cookie(phpsessid_from_cookie(settings.dashboard_session_cookie))}")

    if not settings.dashboard_session_cookie:
        print(
            "\nSet DASHBOARD_SESSION_COOKIE in .env (from DevTools Copy as cURL).\n"
            "Then set DATA_SOURCE_MODE=dashboard_api and restart uvicorn."
        )
        return 1

    repo = DashboardApiRepository()
    try:
        rows = await repo.execute_report(
            report_id=args.report_id,
            sql_table_name=args.table,
            report_name="test",
            bound_filters={},
            user_id=args.user_id,
            access_level=50,
        )
    except DashboardApiError as exc:
        print(f"\nDashboard API error: {exc}")
        return 1

    print(f"\nOK — {len(rows)} row(s)")
    print(json.dumps(rows[:3], indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
