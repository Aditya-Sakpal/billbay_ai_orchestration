import json
import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import text

from app.agent.pipeline_log import log_stage
from app.agent.report_keywords import match_report_id_by_keywords
from app.agent.state import AgentState
from app.config import get_settings
from app.database import AsyncSessionLocal
from app.embeddings import embed_text
from app.llm import get_chat_anthropic

logger = logging.getLogger("vlang.pipeline")

RERANK_SYSTEM_PROMPT = """You are a report selector for a business intelligence system. Given a user question and a list of candidate reports, return the index (0-based) of the single best matching report.

Rules:
- Questions about quota, target, tracking against quota, or SO invoiced vs quota → pick "Sales Quota vs Target"
- Questions about monthly sales, sales performance, or a named salesperson's sales → pick "Monthly Sales Performance (SO)"
- Questions about monthly revenue by department (not a named salesperson) → pick "Gross Margin Analysis (YoY)" or "Key Account Performance"
- Questions about overdue, aging, past due → pick "Overdue Accounts"
- Questions about open/unpaid invoices → pick "Outstanding Invoices"
- If the user names a person (e.g. Karen Ku, Louis Teo), pick "Monthly Sales Performance (SO)" unless they clearly ask about invoices or overdue accounts for that person.

Respond with a JSON object only. No explanation.
Format:
{"best_index": 0}"""

NO_MATCH_MESSAGE = "I could not find a report that matches your question."
PERMISSION_MESSAGE = "You do not have permission to access this report."
NEW_TOPIC_TRIGGERS = (
    "show me",
    "tell me",
    "what is",
    "what's",
    "what are",
    "give me",
    "which",
    "how is",
    "how did",
    "list",
    "find",
)


def _is_follow_up_turn(state: AgentState) -> bool:
    prior_report_id = state.get("resolved_report_id") or state.get(
        "session_report_id"
    )
    if prior_report_id is None:
        return False

    messages = state.get("messages") or []
    if len(messages) <= 1:
        return False

    question_lower = state["current_question"].lower()
    return not any(trigger in question_lower for trigger in NEW_TOPIC_TRIGGERS)


def _parse_llm_json(content: str) -> dict:
    raw = content.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if fence_match:
        raw = fence_match.group(1)
    return json.loads(raw)


async def _embed_question(question: str) -> list[float]:
    return await embed_text(question)


async def _vector_search(
    question_embedding: list[float],
    user_access_level: int,
) -> list[dict]:
    embedding_literal = "[" + ",".join(str(value) for value in question_embedding) + "]"
    sql = text(
        """
        SELECT id, report_name, "group", access_level,
               1 - (name_embedding <=> CAST(:query_embedding AS vector)) AS similarity
        FROM catalog_reports
        WHERE active = 'Y'
          AND access_level <= :user_access_level
          AND name_embedding IS NOT NULL
        ORDER BY similarity DESC
        LIMIT 5
        """
    )
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            sql,
            {
                "query_embedding": embedding_literal,
                "user_access_level": user_access_level,
            },
        )
        return [dict(row) for row in result.mappings().all()]


async def _fetch_report_by_id(report_id: int) -> dict | None:
    sql = text(
        """
        SELECT id, report_name, "group", access_level
        FROM catalog_reports
        WHERE active = 'Y' AND id = :report_id
        """
    )
    async with AsyncSessionLocal() as session:
        result = await session.execute(sql, {"report_id": report_id})
        row = result.mappings().first()
        return dict(row) if row else None


def _boost_quota_candidates(question: str, candidates: list[dict]) -> list[dict]:
    q = question.lower()
    if not any(term in q for term in ("quota", "target", "tracking against")):
        return candidates

    quota = next((c for c in candidates if c.get("id") == 6), None)
    if quota is None:
        return candidates

    others = [c for c in candidates if c.get("id") != 6]
    return [quota, *others]


def _is_salesperson_sales_question(question: str) -> bool:
    q = question.lower()
    if any(term in q for term in ("invoice", "overdue", "aging", "past due", "quota")):
        return False
    if "sales performance" in q or "sales for" in q or "sales of" in q:
        return True
    if re.search(r"\b(for|of)\s+[a-z]+\s+[a-z]+\b", q) and "sales" in q:
        return True
    return bool(re.search(r"\b(for|of)\s+[a-z]+\s+[a-z]+\b", q) and "performance" in q)


async def _boost_sales_perf_candidates(
    question: str,
    candidates: list[dict],
) -> list[dict]:
    if not _is_salesperson_sales_question(question):
        return candidates

    sales = next((c for c in candidates if c.get("id") == 1), None)
    if sales is None:
        sales = await _fetch_report_by_id(1)
    if sales is None:
        return candidates

    others = [c for c in candidates if c.get("id") != 1]
    return [sales, *others]


def _build_candidate_prompt(question: str, candidates: list[dict]) -> str:
    lines = [f"Question: {question}", "", "Candidates:"]
    for index, candidate in enumerate(candidates):
        lines.append(f"{index}: {candidate['report_name']}")
    return "\n".join(lines)


async def _rerank_candidates(question: str, candidates: list[dict]) -> int:
    llm = get_chat_anthropic(model="claude-haiku-4-5")
    response = await llm.ainvoke(
        [
            SystemMessage(content=RERANK_SYSTEM_PROMPT),
            HumanMessage(content=_build_candidate_prompt(question, candidates)),
        ]
    )
    parsed = _parse_llm_json(response.content)
    best_index = int(parsed["best_index"])
    if best_index < 0 or best_index >= len(candidates):
        raise ValueError(f"Invalid best_index: {best_index}")
    return best_index


async def _resolve_by_keywords(question: str) -> dict | None:
    report_id = match_report_id_by_keywords(question)
    if report_id is None:
        return None
    report = await _fetch_report_by_id(report_id)
    if not report:
        return None
    log_stage(
        "resolver",
        method="keyword_fallback",
        report_id=report["id"],
        report_name=report["report_name"],
    )
    return {
        "resolved_report_id": report["id"],
        "resolved_report_name": report["report_name"],
        "session_report_id": report["id"],
        "session_report_name": report["report_name"],
        "error": None,
    }


async def resolver_node(state: AgentState) -> dict:
    if state.get("error"):
        return {}

    try:
        if _is_follow_up_turn(state):
            report_id = state.get("resolved_report_id") or state.get(
                "session_report_id"
            )
            report_name = state.get("resolved_report_name") or state.get(
                "session_report_name"
            )
            log_stage(
                "resolver",
                method="follow_up",
                report_id=report_id,
                report_name=report_name,
            )
            return {
                "resolved_report_id": report_id,
                "resolved_report_name": report_name,
                "error": None,
            }

        question = state["current_question"]
        try:
            question_embedding = await _embed_question(question)
            candidates = await _vector_search(
                question_embedding,
                state["access_level"],
            )
        except Exception as embed_exc:
            logger.warning("Embedding search failed: %s", embed_exc)
            keyword_result = await _resolve_by_keywords(question)
            if keyword_result:
                return keyword_result
            if "quota" in str(embed_exc).lower() or "429" in str(embed_exc):
                return {
                    "error": "Report search unavailable (OpenAI embedding quota exceeded).",
                    "answer": (
                        "Report matching is temporarily unavailable because the OpenAI "
                        "embedding quota is exceeded. Update OPENAI_API_KEY billing or set "
                        "EMBEDDING_PROVIDER=local in .env."
                    ),
                }
            raise

        if any(
            term in question.lower()
            for term in ("quota", "target", "tracking against")
        ):
            quota_report = await _fetch_report_by_id(6)
            if quota_report and not any(c.get("id") == 6 for c in candidates):
                candidates = [quota_report, *candidates[:4]]

        candidates = _boost_quota_candidates(question, candidates)
        candidates = await _boost_sales_perf_candidates(question, candidates)

        if not candidates:
            keyword_result = await _resolve_by_keywords(question)
            if keyword_result:
                return keyword_result
            return {
                "error": "No matching report found for your question.",
                "answer": NO_MATCH_MESSAGE,
            }

        best_index = await _rerank_candidates(question, candidates)
        winning_report = candidates[best_index]

        if winning_report["access_level"] > state["access_level"]:
            return {
                "error": PERMISSION_MESSAGE,
                "answer": PERMISSION_MESSAGE,
            }

        log_stage(
            "resolver",
            method="vector_search",
            report_id=winning_report["id"],
            report_name=winning_report["report_name"],
            candidates=len(candidates),
        )
        return {
            "resolved_report_id": winning_report["id"],
            "resolved_report_name": winning_report["report_name"],
            "session_report_id": winning_report["id"],
            "session_report_name": winning_report["report_name"],
            "error": None,
        }
    except Exception as exc:
        logger.exception("Resolver failed: %s", exc)
        keyword_result = await _resolve_by_keywords(state["current_question"])
        if keyword_result:
            return keyword_result
        return {
            "error": "No matching report found for your question.",
            "answer": NO_MATCH_MESSAGE,
        }
