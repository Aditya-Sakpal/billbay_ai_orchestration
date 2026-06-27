"""Analyze dashboard HTML structure (counts only, no raw HTML output)."""

from __future__ import annotations

import re

import httpx

from app.config import get_settings
from app.repositories.dashboard_api_repository import DashboardApiRepository


def _cell(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


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

    repo = DashboardApiRepository()
    tables = re.findall(r"<table[^>]*>(.*?)</table>", html, re.I | re.S)
    print("tables", len(html))

    for i, table_html in enumerate(tables):
        if "Karen Ku" not in table_html and "Louis Teo" not in table_html:
            continue
        rows = repo._parse_table_block(table_html)
        print(f"table {i} mentions reps, parsed rows:", len(rows))
        if rows:
            print("  headers:", list(rows[0].keys())[:6])
            print("  first row keys sample:", list(rows[0].values())[:3])

    scripts_with_karen = sum(
        1 for s in re.findall(r"<script[^>]*>(.*?)</script>", html, re.I | re.S) if "Karen Ku" in s
    )
    print("scripts containing Karen Ku:", scripts_with_karen)

    merged = repo._parse_html_sales_perf(html)
    names = [
        repo._salesperson_cell(r)
        for r in merged
        if repo._is_salesperson_name(repo._salesperson_cell(r))
    ]
    print("merged sales perf:", len(merged), "reps:", len(names), names[:10])

    form_names = sorted(
        {
            m.group(1)
            for m in re.finditer(r"""name=['"]([^'"]+)['"]""", html, re.I)
            if any(k in m.group(1).lower() for k in ("sales", "person", "report", "action", "period"))
        }
    )
    print("form fields sample:", form_names[:20])

    ajax_urls = sorted(
        {
            m.group(1)
            for m in re.finditer(r"""['"]([^'"]*dashboard\.php[^'"]*)['"]""", html, re.I)
        }
    )
    print("dashboard.php refs:", len(ajax_urls), ajax_urls[:8])

    options = re.findall(r"<option[^>]*>([^<]+)</option>", html, re.I)
    rep_options = [o.strip() for o in options if re.search(r"[A-Za-z]", o) and len(o.strip()) > 3]
    print("select options:", len(rep_options), rep_options[:12])

    for params in [
        {"salesperson": "Karen Ku"},
        {"sp": "Karen Ku"},
        {"Salesperson": "Karen Ku"},
    ]:
        r = httpx.get(
            "https://csportal.billbay.co/dashboard.php",
            headers=headers,
            params=params,
            follow_redirects=True,
            timeout=30,
        )
        rows = repo._parse_html_sales_perf(r.text)
        names = [
            repo._salesperson_cell(x)
            for x in rows
            if repo._is_salesperson_name(repo._salesperson_cell(x))
        ]
        print("GET params", params, "-> reps", names[:5])

    post_headers = {**headers, "X-Requested-With": "XMLHttpRequest"}
    for data in [{}, {"action": "load"}, {"action": "sales_performance"}]:
        r = httpx.post(
            "https://csportal.billbay.co/dashboard.php",
            headers=post_headers,
            data=data,
            follow_redirects=True,
            timeout=30,
        )
        rows = repo._parse_html_sales_perf(r.text)
        names = [
            repo._salesperson_cell(x)
            for x in rows
            if repo._is_salesperson_name(repo._salesperson_cell(x))
        ]
        print("POST data", data, "status", r.status_code, "reps", len(names), names[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
