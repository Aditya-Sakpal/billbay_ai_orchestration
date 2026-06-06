import json
import re

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.config import get_settings

SYSTEM_PROMPT = """You are an intent classifier for a business intelligence system. Your job is to decide if a user question can be answered using sales, finance, inventory, purchasing, POS, or master data reports.

Follow-up questions (e.g. "same for Karen Ku", "what about last year", "show me that for another rep") are in scope when they continue an earlier report question in the conversation.

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


def _build_user_content(state: AgentState) -> str:
    parts: list[str] = []
    prior_domain = state.get("intent_domain")
    bound_filters = state.get("bound_filters") or {}
    messages = state.get("messages") or []

    if prior_domain or bound_filters:
        context_bits = []
        if prior_domain:
            context_bits.append(f"prior domain: {prior_domain}")
        if bound_filters:
            context_bits.append(f"active filters: {json.dumps(bound_filters)}")
        parts.append("Session context: " + "; ".join(context_bits))

    if len(messages) > 1:
        history_lines = []
        for msg in messages[-6:-1]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_lines.append(f"{role}: {content}")
        if history_lines:
            parts.append("Recent conversation:\n" + "\n".join(history_lines))

    parts.append(f"Current question: {state['current_question']}")
    return "\n\n".join(parts)


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
                HumanMessage(content=_build_user_content(state)),
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
