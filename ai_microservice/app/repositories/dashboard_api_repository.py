"""
Live Cornerstone BI dashboard API client (Option A).

Configure via .env after capturing Copy-as-cURL from csportal.billbay.co DevTools.
Endpoint mapping per report: data/dashboard_api_endpoints.json
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any

import httpx

from app.agent.pipeline_log import log_stage
from app.dashboard_auth import mask_cookie, mask_headers, phpsessid_from_cookie, refresh_dashboard_settings

QUERY_TIMEOUT_SECONDS = 30
ENDPOINTS_FILE = Path(__file__).resolve().parents[2] / "data" / "dashboard_api_endpoints.json"
PERIOD_LABEL_RE = re.compile(r"^\d{4}\.\d{1,2}$")
SALESPERSON_COLS = ("Salesperson", "salesperson")


class DashboardApiError(Exception):
    pass


class DashboardApiRepository:
    def __init__(self) -> None:
        self._endpoints = self._load_endpoints()
        self._settings = refresh_dashboard_settings()

    def _reload_settings(self) -> None:
        """Pick up DASHBOARD_SESSION_COOKIE changes from .env on every request."""
        self._settings = refresh_dashboard_settings()

    @staticmethod
    def _load_endpoints() -> dict[str, Any]:
        if not ENDPOINTS_FILE.exists():
            return {}
        return json.loads(ENDPOINTS_FILE.read_text(encoding="utf-8"))

    def _build_url(self, endpoint_path: str) -> str:
        if endpoint_path.startswith("http"):
            return endpoint_path
        base = self._settings.dashboard_base_url.rstrip("/")
        path = endpoint_path if endpoint_path.startswith("/") else f"/{endpoint_path}"
        return f"{base}{path}"

    def _default_headers(self, endpoint_cfg: dict[str, Any] | None = None) -> dict[str, str]:
        cfg = endpoint_cfg or {}
        headers = {
            "Accept": cfg.get("accept") or "application/json, text/javascript, */*; q=0.01",
            "Referer": self._settings.dashboard_referer,
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            ),
        }
        if cfg.get("response_mode") != "html_table":
            headers["X-Requested-With"] = "XMLHttpRequest"
        if self._settings.dashboard_session_cookie:
            headers["Cookie"] = self._settings.dashboard_session_cookie
        return headers

    def _resolve_endpoint(self, sql_table_name: str, report_id: int) -> dict[str, Any]:
        by_table = self._endpoints.get("reports", {}).get(sql_table_name)
        if by_table:
            return by_table

        by_id = self._endpoints.get("reports_by_id", {}).get(str(report_id))
        if by_id:
            return by_id

        default = self._endpoints.get("default")
        if default:
            return default

        raise DashboardApiError(
            f"No dashboard API mapping for report table '{sql_table_name}' (id={report_id}). "
            "Update data/dashboard_api_endpoints.json after capturing DevTools cURL."
        )

    def _build_payload(
        self,
        endpoint_cfg: dict[str, Any],
        bound_filters: dict[str, Any],
        user_id: int,
    ) -> dict[str, Any]:
        payload = dict(endpoint_cfg.get("payload_template") or {})
        filter_mapping: dict[str, str] = endpoint_cfg.get("filter_mapping") or {}

        for filter_key, filter_value in bound_filters.items():
            api_key = filter_mapping.get(filter_key, filter_key)
            payload[api_key] = filter_value

        if endpoint_cfg.get("include_user_id", True):
            user_key = endpoint_cfg.get("user_id_param", "user_id")
            payload.setdefault(user_key, user_id)

        return payload

    @staticmethod
    def _extract_rows(payload: Any, rows_path: str | None) -> Any:
        if rows_path:
            current: Any = payload
            for part in rows_path.split("."):
                if not isinstance(current, dict):
                    break
                current = current.get(part)
            if current is not None:
                return current

        if isinstance(payload, list):
            return payload

        if isinstance(payload, dict):
            for key in ("rows", "data", "aaData", "records", "result", "items"):
                if isinstance(payload.get(key), list):
                    return payload[key]
            if isinstance(payload.get("data"), dict):
                nested = payload["data"]
                for key in ("rows", "records", "items"):
                    if isinstance(nested.get(key), list):
                        return nested[key]

        return payload

    @staticmethod
    def _normalize_rows(raw_rows: Any, columns: list[str] | None) -> list[dict[str, Any]]:
        if not raw_rows:
            return []

        if isinstance(raw_rows, list) and raw_rows and isinstance(raw_rows[0], dict):
            return [dict(row) for row in raw_rows]

        if isinstance(raw_rows, list) and raw_rows and isinstance(raw_rows[0], (list, tuple)):
            if not columns:
                columns = [f"col_{i}" for i in range(len(raw_rows[0]))]
            return [dict(zip(columns, row)) for row in raw_rows]

        if isinstance(raw_rows, str):
            return [{"html": raw_rows}]

        raise DashboardApiError(f"Unrecognized dashboard response row format: {type(raw_rows)}")

    def _parse_table_block(self, table_html: str) -> list[dict[str, Any]]:
        """Parse one table with or without thead/tbody."""
        headers: list[str] = []
        body_html = table_html

        header_match = re.search(r"<thead[^>]*>(.*?)</thead>", table_html, re.DOTALL | re.IGNORECASE)
        body_match = re.search(r"<tbody[^>]*>(.*?)</tbody>", table_html, re.DOTALL | re.IGNORECASE)
        if header_match and body_match:
            headers = [
                re.sub(r"<[^>]+>", "", h).strip()
                for h in re.findall(r"<th[^>]*>(.*?)</th>", header_match.group(1), re.DOTALL | re.IGNORECASE)
            ]
            body_html = body_match.group(1)
        else:
            rows_html = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, re.DOTALL | re.IGNORECASE)
            if not rows_html:
                return []
            first_cells = re.findall(
                r"<t[dh][^>]*>(.*?)</t[dh]>",
                rows_html[0],
                re.DOTALL | re.IGNORECASE,
            )
            first_cells = [re.sub(r"<[^>]+>", "", c).strip() for c in first_cells]
            if first_cells and any(re.search(r"sales|trade|margin", c, re.I) for c in first_cells):
                headers = first_cells
                body_html = "".join(f"<tr>{row}</tr>" for row in rows_html[1:])
            else:
                body_html = "".join(f"<tr>{row}</tr>" for row in rows_html)

        if not headers:
            return []

        rows: list[dict[str, Any]] = []
        for row_html in re.findall(r"<tr[^>]*>(.*?)</tr>", body_html, re.DOTALL | re.IGNORECASE):
            cells = re.findall(
                r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, re.DOTALL | re.IGNORECASE
            )
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            if cells and len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        return rows

    @staticmethod
    def _looks_like_sales_perf_table(rows: list[dict[str, Any]]) -> bool:
        if not rows:
            return False
        headers = {key.lower() for key in rows[0].keys()}
        return "salesperson" in headers and any("sales" in key for key in headers)

    def _sales_perf_headers(self, html: str) -> list[str] | None:
        for header_match in re.finditer(
            r"<thead[^>]*>(.*?)</thead>", html, re.DOTALL | re.IGNORECASE
        ):
            headers = [
                re.sub(r"<[^>]+>", "", h).strip()
                for h in re.findall(
                    r"<th[^>]*>(.*?)</th>",
                    header_match.group(1),
                    re.DOTALL | re.IGNORECASE,
                )
            ]
            if not headers:
                continue
            if headers[0].lower() != "salesperson":
                continue
            if not any("sales" in header.lower() for header in headers):
                continue
            return headers
        return None

    def _parse_showdetails_sales_rows(self, html: str) -> list[dict[str, Any]]:
        """
        Cornerstone dashboard embeds all rep summary rows as:
        <tr onclick="showDetails('id')"><td>Name</td><td>Sales</td>...
        """
        headers = self._sales_perf_headers(html)
        if not headers:
            return []

        rows: list[dict[str, Any]] = []
        for row_html in re.findall(
            r'<tr[^>]*onclick="showDetails\([^"]*\)"[^>]*>(.*?)</tr>',
            html,
            re.DOTALL | re.IGNORECASE,
        ):
            cells = re.findall(r"<td[^>]*>(.*?)</td>", row_html, re.DOTALL | re.IGNORECASE)
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            if cells and len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        return rows

    def _parse_html_sales_perf(self, html: str) -> list[dict[str, Any]]:
        """Collect all salesperson summary rows from the live dashboard HTML."""
        summary_rows = self._parse_showdetails_sales_rows(html)
        if summary_rows:
            return summary_rows

        tables = re.findall(r"<table[^>]*>(.*?)</table>", html, re.DOTALL | re.IGNORECASE)
        merged: list[dict[str, Any]] = []
        seen_summary: set[str] = set()

        for table_html in tables:
            rows = self._parse_table_block(table_html)
            if not self._looks_like_sales_perf_table(rows):
                continue
            for row in rows:
                label = self._salesperson_cell(row)
                if self._is_salesperson_name(label):
                    key = label.lower()
                    if key in seen_summary:
                        continue
                    seen_summary.add(key)
                    merged.append(row)
                elif self._is_period_label(label):
                    merged.append(row)

        if merged:
            return merged

        match_headers = ["Salesperson", "salesperson", "Sales ($)"]
        return self._parse_html_table(html, match_headers)

    def _parse_html_table(
        self,
        html: str,
        match_headers: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Parse HTML tables; prefer one whose headers match report columns."""
        tables = re.findall(
            r"<table[^>]*>(.*?)</table>", html, re.DOTALL | re.IGNORECASE
        )
        best_rows: list[dict[str, Any]] = []
        best_score = -1

        for table_html in tables:
            header_match = re.search(
                r"<thead[^>]*>(.*?)</thead>", table_html, re.DOTALL | re.IGNORECASE
            )
            body_match = re.search(
                r"<tbody[^>]*>(.*?)</tbody>", table_html, re.DOTALL | re.IGNORECASE
            )
            if not header_match or not body_match:
                continue

            headers = re.findall(
                r"<th[^>]*>(.*?)</th>", header_match.group(1), re.DOTALL | re.IGNORECASE
            )
            headers = [re.sub(r"<[^>]+>", "", h).strip() for h in headers]
            if not headers:
                continue

            rows: list[dict[str, Any]] = []
            for row_html in re.findall(
                r"<tr[^>]*>(.*?)</tr>", body_match.group(1), re.DOTALL | re.IGNORECASE
            ):
                cells = re.findall(
                    r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, re.DOTALL | re.IGNORECASE
                )
                cells = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
                if cells and len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))

            if not rows:
                continue

            summary_count = sum(
                1 for row in rows if self._is_salesperson_name(self._salesperson_cell(row))
            )
            score = summary_count * 100 + len(rows)
            if match_headers:
                lowered = {h.lower() for h in headers}
                score += sum(10 for needle in match_headers if needle.lower() in lowered)

            if score > best_score:
                best_score = score
                best_rows = rows

        return best_rows

    @staticmethod
    def _salesperson_cell(row: dict[str, Any]) -> str:
        for key in SALESPERSON_COLS:
            if key in row and row[key] is not None:
                return str(row[key]).strip()
        return ""

    @classmethod
    def _is_period_label(cls, value: str) -> bool:
        return bool(PERIOD_LABEL_RE.match(value.strip()))

    @classmethod
    def _is_salesperson_name(cls, value: str) -> bool:
        value = value.strip()
        if not value or cls._is_period_label(value):
            return False
        return bool(re.search(r"[A-Za-z]", value))

    @classmethod
    def _postprocess_sales_perf_rows(
        cls,
        rows: list[dict[str, Any]],
        bound_filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Live dashboard HTML interleaves summary rows (rep names) with period rows
        (2026.5, 2025.12, …) in the Salesperson column when a rep is expanded.
        """
        salesperson_filter = (
            bound_filters.get("salesperson")
            or bound_filters.get("Salesperson")
            or ""
        ).strip()

        if salesperson_filter:
            needle = salesperson_filter.lower()
            matched = [
                row
                for row in rows
                if needle in cls._salesperson_cell(row).lower()
            ]
            if matched:
                return matched
            raise DashboardApiError(
                f"No live dashboard data found for '{salesperson_filter}'. "
                "Refresh DASHBOARD_SESSION_COOKIE in .env (log in and run apply_captured_curl)."
            )

        return [
            row
            for row in rows
            if cls._is_salesperson_name(cls._salesperson_cell(row))
        ]

    @classmethod
    def _extract_salesperson_block(
        cls,
        rows: list[dict[str, Any]],
        salesperson: str,
    ) -> list[dict[str, Any]]:
        needle = salesperson.lower()
        result: list[dict[str, Any]] = []
        in_block = False
        matched_name = ""

        for row in rows:
            label = cls._salesperson_cell(row)
            if cls._is_salesperson_name(label):
                if needle in label.lower():
                    in_block = True
                    matched_name = label
                    result.append(dict(row))
                elif in_block:
                    break
            elif in_block and cls._is_period_label(label):
                period_row = dict(row)
                period_row["Period"] = label
                period_row["Salesperson"] = matched_name
                result.append(period_row)

        return result

    @staticmethod
    def _looks_like_login_page(html: str, url: str) -> bool:
        lowered_url = url.lower()
        if "st=ses" in lowered_url:
            return True
        if "/index.php" in lowered_url and "dashboard.php" not in lowered_url:
            return True
        lowered = html.lower()
        if re.search(r"<title[^>]*>[^<]*login", html, re.I):
            return True
        if re.search(r"type=[\"']password[\"']", html, re.I):
            if "showdetails" not in lowered and "salesperson" not in lowered:
                return True
        return False

    @staticmethod
    def _redirected_to_login(response: httpx.Response) -> bool:
        for hop in response.history:
            location = str(hop.headers.get("location", ""))
            if DashboardApiRepository._looks_like_login_page("", location):
                return True
        return False

    @staticmethod
    def _session_expired_message() -> str:
        return (
            "Session expired — log in at csportal.billbay.co, copy a fresh cURL into "
            "captured.curl, run: python -m scripts.apply_captured_curl, then retry "
            "(uvicorn reloads the cookie automatically on the next request)."
        )

    async def _request(
        self,
        url: str,
        method: str,
        payload: dict[str, Any],
        extra_headers: dict[str, str] | None,
        endpoint_cfg: dict[str, Any] | None = None,
    ) -> Any:
        self._reload_settings()
        headers = self._default_headers(endpoint_cfg)
        if extra_headers:
            headers.update(extra_headers)

        log_stage(
            "dashboard_api",
            event="request",
            url=url,
            method=method,
            headers=mask_headers(headers),
            cookie=mask_cookie(self._settings.dashboard_session_cookie),
        )

        timeout = httpx.Timeout(self._settings.dashboard_api_timeout)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            method_upper = method.upper()
            if method_upper == "GET":
                response = await client.get(url, headers=headers, params=payload)
            else:
                content_type = headers.get("Content-Type", "")
                if "application/json" in content_type:
                    response = await client.post(url, headers=headers, json=payload)
                else:
                    response = await client.post(url, headers=headers, data=payload)

        final_url = str(response.url)
        text = response.text
        body_preview = text[:500]

        log_stage(
            "dashboard_api",
            event="response",
            url=final_url,
            status=response.status_code,
            body_preview=body_preview,
        )

        if self._redirected_to_login(response) or self._looks_like_login_page(text, final_url):
            raise DashboardApiError(self._session_expired_message())

        if response.status_code >= 400:
            raise DashboardApiError(
                f"Dashboard API HTTP {response.status_code}: {body_preview}"
            )

        if endpoint_cfg and endpoint_cfg.get("response_mode") == "html_table":
            match_headers = endpoint_cfg.get("table_match_headers") or ["Salesperson", "salesperson"]
            if endpoint_cfg.get("html_parser") == "sales_perf":
                rows = self._parse_html_sales_perf(text)
            else:
                rows = self._parse_html_table(text, match_headers)
            if not rows and self._looks_like_login_page(text, final_url):
                raise DashboardApiError(self._session_expired_message())
            if not rows:
                raise DashboardApiError(
                    "No matching HTML table found on dashboard page. "
                    "Capture the XHR request from DevTools (Fetch/XHR filter) instead."
                )
            return rows

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()

        if "<table" in text.lower():
            return self._parse_html_table(text)
        try:
            return response.json()
        except json.JSONDecodeError:
            return text

    async def execute_report(
        self,
        report_id: int,
        sql_table_name: str,
        report_name: str,
        bound_filters: dict,
        user_id: int,
        access_level: int,
    ) -> list[dict]:
        self._reload_settings()
        cookie = self._settings.dashboard_session_cookie
        log_stage(
            "dashboard_api",
            event="auth",
            cookie=mask_cookie(cookie),
            phpsessid=mask_cookie(phpsessid_from_cookie(cookie)),
        )
        if not cookie:
            raise DashboardApiError(
                "DASHBOARD_SESSION_COOKIE is not set. "
                "Copy the cookie header from DevTools cURL into ai_microservice/.env"
            )

        endpoint_cfg = self._resolve_endpoint(sql_table_name, report_id)
        url = self._build_url(
            endpoint_cfg.get("url") or self._settings.dashboard_api_url
        )
        if not url:
            raise DashboardApiError(
                "dashboard_api_url is empty. Set DASHBOARD_API_URL in .env"
            )

        method = endpoint_cfg.get("method") or self._settings.dashboard_api_method
        payload = self._build_payload(endpoint_cfg, bound_filters, user_id)
        extra_headers = endpoint_cfg.get("headers") or {}
        if endpoint_cfg.get("content_type"):
            extra_headers.setdefault("Content-Type", endpoint_cfg["content_type"])

        log_stage(
            "dashboard_api",
            url=url,
            method=method,
            report_id=report_id,
            sql_table=sql_table_name,
            bound_filters=bound_filters,
        )

        raw = await asyncio.wait_for(
            self._request(url, method, payload, extra_headers, endpoint_cfg),
            timeout=self._settings.dashboard_api_timeout,
        )

        if isinstance(raw, list) and raw and isinstance(raw[0], dict):
            if sql_table_name == "bbz_sales_perf":
                rows = self._postprocess_sales_perf_rows(raw, bound_filters)
            else:
                rows = raw
            log_stage("dashboard_api", rows_returned=len(rows), source="html_showDetails")
            return rows

        rows_path = endpoint_cfg.get("response_rows_path")
        columns = endpoint_cfg.get("response_columns")
        raw_rows = self._extract_rows(raw, rows_path)
        return self._normalize_rows(raw_rows, columns)

    async def get_lookup_values(
        self,
        table: str,
        column: str,
        user_id: int,
    ) -> list[str]:
        # Optional: add lookup endpoints to dashboard_api_endpoints.json later.
        return []
