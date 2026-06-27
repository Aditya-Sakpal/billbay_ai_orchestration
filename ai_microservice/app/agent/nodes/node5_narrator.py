from langchain_core.messages import HumanMessage, SystemMessage
import re

from app.agent.pipeline_log import log_stage
from app.agent.state import AgentState
from app.config import get_settings
from app.llm import get_chat_anthropic

# TODO: optimise model selection (Haiku vs Sonnet) based on row count in Week 3
NARRATOR_MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """You are a business intelligence assistant. You have just run a report and received data rows. Write a SHORT, clear natural language summary of the key insights from the data.

Rules:
- Maximum 3 sentences for the summary.
- Do not repeat every row — highlight the most important insight only.
- After the summary, the data table will be appended automatically. Do not reproduce the table in your summary.
- Be direct. No filler phrases like "Based on the data provided".
- If a Period column is present, those rows are monthly breakdown for the Salesperson named in the same row.
- If the question names a specific salesperson, summarize that person's data only.
- Do not claim a salesperson is missing when their rows are present in the data."""


def _strip_markdown_tables(text: str) -> str:
    """Remove pipe-style markdown tables; narrator appends the canonical table separately."""
    lines = text.splitlines()
    kept: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("|") and line.endswith("|"):
            index += 1
            while index < len(lines) and lines[index].strip().startswith("|"):
                index += 1
            continue
        kept.append(lines[index])
        index += 1
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()


def _rows_to_markdown_table(rows: list[dict]) -> str:
    if not rows:
        return ""

    headers = list(rows[0].keys())
    header_row = "| " + " | ".join(str(header) for header in headers) + " |"
    separator_row = "| " + " | ".join("---" for _ in headers) + " |"
    data_rows = [
        "| " + " | ".join(str(row.get(header, "")) for header in headers) + " |"
        for row in rows
    ]
    return "\n".join([header_row, separator_row, *data_rows])


def _llm_content(response) -> str:
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


def _extract_requested_person_name(question: str) -> str | None:
    patterns = [
        r"(?:sales performance|performance|sales)\s+(?:of|for)\s+([A-Za-z]+(?:\s+[A-Za-z]+)+)",
        r"(?:for|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, question)
        if match:
            return match.group(1).strip()
    return None


def _result_does_not_match_person(rows: list[dict], requested_name: str) -> str | None:
    needle = requested_name.lower()
    period_re = re.compile(r"^\d{4}\.\d{1,2}$")
    for row in rows:
        for key in ("Salesperson", "salesperson"):
            value = str(row.get(key, "")).strip()
            if value and needle in value.lower():
                return None
    for row in rows:
        for key in ("Salesperson", "salesperson"):
            value = str(row.get(key, "")).strip()
            if not value or period_re.match(value):
                continue
            if re.search(r"[A-Za-z]", value):
                return value
    return None


async def narrator_node(state: AgentState) -> dict:
    if state.get("error") and state.get("answer"):
        return {}

    if state.get("error"):
        return {"answer": state["error"]}

    query_result = state.get("query_result", [])
    question = state.get("current_question") or ""
    question_lower = question.lower()

    requested_name = _extract_requested_person_name(question)
    if requested_name and query_result:
        mismatch = _result_does_not_match_person(query_result, requested_name)
        if mismatch:
            return {
                "answer": (
                    f"I couldn't find live dashboard data for **{requested_name}**. "
                    f"The page scrape only returned data for **{mismatch}**. "
                    "Try capturing the dashboard.php XHR request from DevTools "
                    "(Network → Fetch/XHR) while that salesperson's row is visible on the dashboard."
                ),
                "error": None,
            }

    if not query_result:
        question = (state.get("current_question") or "").lower()
        if state.get("error"):
            return {"answer": state["error"]}
        demo_reps = "Aelina Senitro, Louis Teo, Karen Ku, Elaine Yeo"
        if any(name in question for name in ("krishnan", "shamini")):
            return {
                "answer": (
                    f"No data found for that salesperson. "
                    f"Demo data includes: {demo_reps}."
                )
            }
        return {"answer": "No data found for your query."}

    markdown_table = _rows_to_markdown_table(query_result)
    preview_table = _rows_to_markdown_table(query_result[:50])
    question_lower = (state.get("current_question") or "").lower()
    partial_live_note = ""
    if (
        "all" in question_lower
        and "sales" in question_lower
        and len(query_result) <= 2
        and get_settings().data_source_mode == "dashboard_api"
    ):
        partial_live_note = (
            "\n\n_Note: live dashboard HTML currently returns a partial sales table. "
            "Capture the dashboard.php XHR request from DevTools to load all salespersons._"
        )

    try:
        llm = get_chat_anthropic(model=NARRATOR_MODEL)
        user_prompt = (
            f"Report: {state.get('resolved_report_name', 'Report')}\n"
            f"Question: {state.get('current_question', '')}\n\n"
            f"Data ({len(query_result)} rows):\n"
            f"{preview_table}"
        )
        response = await llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
        )
        sonnet_response = _strip_markdown_tables(_llm_content(response).strip())
        final_answer = (
            f"{sonnet_response}{partial_live_note}\n\n**Source data:**\n{markdown_table}"
        )
    except Exception:
        final_answer = (
            "I was unable to generate a summary. Here is the raw data:\n\n"
            + markdown_table
        )

    log_stage(
        "narrator",
        report=state.get("resolved_report_name"),
        rows=len(query_result),
        answer_chars=len(final_answer),
    )

    new_messages = state.get("messages", []) + [
        {"role": "assistant", "content": final_answer}
    ]

    return {
        "answer": final_answer,
        "messages": new_messages,
        "error": None,
    }
