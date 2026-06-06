import json
import re

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import text

from app.agent.state import AgentState
from app.config import get_settings
from app.database import AsyncSessionLocal
from app.embeddings import embed_text

RERANK_SYSTEM_PROMPT = """You are a report selector for a business intelligence system. Given a user question and a list of candidate reports, return the index (0-based) of the single best matching report.

Respond with a JSON object only. No explanation.
Format:
{"best_index": 0}"""

NO_MATCH_MESSAGE = "I could not find a report that matches your question."
PERMISSION_MESSAGE = "You do not have permission to access this report."


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


def _build_candidate_prompt(question: str, candidates: list[dict]) -> str:
    lines = [f"Question: {question}", "", "Candidates:"]
    for index, candidate in enumerate(candidates):
        lines.append(f"{index}: {candidate['report_name']}")
    return "\n".join(lines)


async def _rerank_candidates(question: str, candidates: list[dict], api_key: str) -> int:
    llm = ChatAnthropic(
        model="claude-haiku-4-5",
        api_key=api_key,
    )
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


async def resolver_node(state: AgentState) -> dict:
    if state.get("error"):
        return {}

    settings = get_settings()
    try:
        question_embedding = await _embed_question(
            state["current_question"],
        )
        candidates = await _vector_search(
            question_embedding,
            state["access_level"],
        )

        if not candidates:
            return {
                "error": "No matching report found for your question.",
                "answer": NO_MATCH_MESSAGE,
            }

        best_index = await _rerank_candidates(
            state["current_question"],
            candidates,
            settings.anthropic_api_key,
        )
        winning_report = candidates[best_index]

        if winning_report["access_level"] > state["access_level"]:
            return {
                "error": PERMISSION_MESSAGE,
                "answer": PERMISSION_MESSAGE,
            }

        return {
            "resolved_report_id": winning_report["id"],
            "resolved_report_name": winning_report["report_name"],
            "error": None,
        }
    except Exception:
        return {
            "error": "No matching report found for your question.",
            "answer": NO_MATCH_MESSAGE,
        }
