"""Debug sales performance HTML parsing."""

from __future__ import annotations

import re

import httpx

from app.config import get_settings
from app.repositories.dashboard_api_repository import DashboardApiRepository


def main() -> int:
    get_settings.cache_clear()
    settings = get_settings()
    headers = {
        "Cookie": settings.dashboard_session_cookie,
        "User-Agent": "Mozilla/5.0",
        "Referer": settings.dashboard_referer,
    }
    html = httpx.get(
        "https://csportal.billbay.co/dashboard.php",
        headers=headers,
        follow_redirects=True,
        timeout=30,
    ).text

    idx = html.find("Sales ($)")
    section = html[max(0, idx - 4000) : idx + 200000] if idx >= 0 else html
    header_match = re.search(r"<thead[^>]*>(.*?)</thead>", section, re.DOTALL | re.IGNORECASE)
    print("idx", idx, "header_match", bool(header_match))
    if header_match:
        headers = [
            re.sub(r"<[^>]+>", "", h).strip()
            for h in re.findall(r"<th[^>]*>(.*?)</th>", header_match.group(1), re.DOTALL | re.IGNORECASE)
        ]
        print("headers", headers[:5], "count", len(headers))
        onclick_rows = re.findall(
            r'<tr[^>]*onclick="showDetails\([^"]*\)"[^>]*>(.*?)</tr>',
            section,
            re.DOTALL | re.IGNORECASE,
        )
        print("onclick rows", len(onclick_rows))
        if onclick_rows:
            cells = re.findall(r"<td[^>]*>(.*?)</td>", onclick_rows[10], re.DOTALL | re.IGNORECASE)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            print("karen row cell count", len(cells), "vs headers", len(headers))
            print("karen cells", cells[:3])

    repo = DashboardApiRepository()
    show_rows = repo._parse_showdetails_sales_rows(html)
    print("showdetails parser:", len(show_rows))
    if show_rows:
        print(" first:", show_rows[0].get("Salesperson"))
        print(" karen:", [r for r in show_rows if "Karen" in r.get("Salesperson", "")])

    parsed = repo._parse_html_sales_perf(html)
    names = [
        repo._salesperson_cell(r)
        for r in parsed
        if repo._is_salesperson_name(repo._salesperson_cell(r))
    ]
    print("parser rep count:", len(names))
    print("parser reps:", names[:20])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
