"""Keyword fallback when embedding search is unavailable (e.g. OpenAI quota)."""

from __future__ import annotations

# (keyword phrases, catalog report id) — mirrors cs_dashboard_menu / dashboard widgets
REPORT_KEYWORD_RULES: list[tuple[tuple[str, ...], int]] = [
    (
        (
            "sales performance",
            "sales perf",
            "last 6 months",
            "monthly sales",
            "salesperson",
            "sales for",
            "sales of",
        ),
        1,
    ),
    (("gross margin", "margin analysis", "revenue by department"), 2),
    (("overdue", "aging", "past due", "max aging"), 3),
    (("outstanding invoice", "open invoice", "unpaid invoice", "amount due"), 4),
    (("payment term", "credit term", "credit limit", "avg pay"), 5),
    (("quota", "target", "tracking against", "so invoiced"), 6),
    (("key account",), 7),
]


def match_report_id_by_keywords(question: str) -> int | None:
    q = question.lower()
    for phrases, report_id in REPORT_KEYWORD_RULES:
        if any(phrase in q for phrase in phrases):
            return report_id
    return None
