import json
import re

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.config import get_settings

SYSTEM_PROMPT = """You are an intent classifier for a business intelligence system. Your job is to decide if a user question can be answered using sales, finance, inventory, purchasing, POS, or master data reports.

Respond with a JSON object only. No explanation.
Format:
{
  "in_scope": true or false,
  "domain": one of ["SALES","FINANCE","INVENTORY","PURCHASES","POS","MASTER DATA","DATA ALERT","UNKNOWN"],
  "reason": "one sentence max"
}"""

OUT_OF_SCOPE_MESSAGE = (
    "I can only answer questions about sales, finance, inventory, "
    "purchasing, POS, or master data reports."
)


def _parse_llm_json(content: str) -> dict:
    text = content.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    return json.loads(text)


async def intent_node(state: AgentState) -> dict:
    if state.get("error"):
        return {}

    turn_reset = {
        "resolved_report_id": None,
        "resolved_report_name": None,
        "query_result": [],
        "answer": "",
        "error": None,
    }

    settings = get_settings()
    try:
        llm = ChatAnthropic(
            model="claude-haiku-4-5",
            api_key=settings.anthropic_api_key,
        )
        response = await llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=state["current_question"]),
            ]
        )
        parsed = _parse_llm_json(response.content)
        in_scope = bool(parsed.get("in_scope"))
        domain = parsed.get("domain")

        if not in_scope:
            return {
                **turn_reset,
                "error": OUT_OF_SCOPE_MESSAGE,
                "answer": OUT_OF_SCOPE_MESSAGE,
            }

        return {
            **turn_reset,
            "error": None,
            "intent_domain": domain,
        }
    except Exception:
        return {
            **turn_reset,
            "error": "Intent classification failed.",
            "answer": "Something went wrong. Please try again.",
        }
