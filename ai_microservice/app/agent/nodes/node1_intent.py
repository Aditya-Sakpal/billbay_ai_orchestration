import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.llm import get_chat_anthropic

SYSTEM_PROMPT = """You are an intent classifier for a business intelligence system. Your job is to decide if a user question can be answered using business reports.

In scope includes questions about:
- Sales and performance (revenue, quotas, salesperson results)
- Finance (margins, revenue, departments, gross margin)
- Collections and accounts receivable (overdue accounts, aging, outstanding invoices, payment terms, credit limits, amounts due)
- Inventory, purchasing, POS, and master data

Follow-up questions (e.g. "same for Karen Ku", "what about last year", "show me that for another rep") are in scope when they continue an earlier report question in the conversation.

Examples that ARE in scope:
- "Show me monthly sales performance"
- "Which customers have overdue accounts?"
- "List outstanding invoices"
- "What are the payment terms for this customer?"

Respond with a JSON object only. No explanation.
Format:
{
  "in_scope": true or false,
  "domain": one of ["SALES","FINANCE","COLLECTIONS","INVENTORY","PURCHASES","POS","MASTER DATA","DATA ALERT","UNKNOWN"],
  "reason": "one sentence max"
}"""

OUT_OF_SCOPE_MESSAGE = (
    "I can only answer questions about sales, finance, collections, inventory, "
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
    turn_reset = {
        "resolved_report_id": None,
        "resolved_report_name": None,
        "query_result": [],
        "answer": "",
        "error": None,
    }

    try:
        llm = get_chat_anthropic(model="claude-haiku-4-5")
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
    except Exception as exc:
        err_text = str(exc).lower()
        if "authentication" in err_text or "401" in err_text or "invalid x-api-key" in err_text:
            message = (
                "Anthropic credentials are invalid. Set ANTHROPIC_API_KEY (sk-ant-...) "
                "or ANTHROPIC_OAUTH_TOKEN in ai_microservice/.env and restart."
            )
        elif "credit" in err_text or "billing" in err_text:
            message = "Anthropic account has insufficient credits."
        else:
            message = "Something went wrong. Please try again."
        return {
            **turn_reset,
            "error": "Intent classification failed.",
            "answer": message,
        }
