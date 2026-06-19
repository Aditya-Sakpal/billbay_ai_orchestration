from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
import re

from app.agent.state import AgentState
from app.config import get_settings

# TODO: optimise model selection (Haiku vs Sonnet) based on row count in Week 3
NARRATOR_MODEL = "claude-sonnet-4-5"

SYSTEM_PROMPT = """You are a business intelligence assistant. You have just run a report and received data rows. Write a SHORT, clear natural language summary of the key insights from the data.

Rules:
- Maximum 3 sentences for the summary.
- Do not repeat every row — highlight the most important insight only.
- After the summary, the data table will be appended automatically. Do not reproduce the table in your summary.
- Be direct. No filler phrases like "Based on the data provided"."""


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


async def narrator_node(state: AgentState) -> dict:
    if state.get("error") and state.get("answer"):
        return {}

    if state.get("error"):
        return {"answer": state["error"]}

    query_result = state.get("query_result", [])
    if not query_result:
        return {"answer": "No data found for your query."}

    markdown_table = _rows_to_markdown_table(query_result)
    preview_table = _rows_to_markdown_table(query_result[:50])

    try:
        settings = get_settings()
        llm = ChatAnthropic(
            model=NARRATOR_MODEL,
            api_key=settings.anthropic_api_key,
        )
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
            f"{sonnet_response}\n\n**Source data:**\n{markdown_table}"
        )
    except Exception:
        final_answer = (
            "I was unable to generate a summary. Here is the raw data:\n\n"
            + markdown_table
        )

    new_messages = state.get("messages", []) + [
        {"role": "assistant", "content": final_answer}
    ]

    return {
        "answer": final_answer,
        "messages": new_messages,
        "error": None,
    }
