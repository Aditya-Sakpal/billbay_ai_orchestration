import datetime
import json
import re

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.config import get_settings
from app.database import AsyncSessionLocal
from app.repositories.catalog_repository import CatalogRepository

ENTITY_KEYS = [
    "salesperson",
    "Salesperson",
    "customer",
    "Customer",
    "department",
    "Department",
    "item",
    "Item",
]


def _parse_llm_json(content: str) -> dict:
    text = content.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    return json.loads(text)


def _build_system_prompt(today: datetime.date) -> str:
    return f"""You are a filter extractor for a business intelligence system. Given a user question and a list of filter fields, extract the values the user is referring to.

Today's date is {today.isoformat()}.
Current year is {today.year}.
Current month number is {today.month}.

Rules:
- For month filters: return the month as an integer (1=January, 12=December).
- For year filters: return 4-digit year as string.
- For salesperson/customer filters: return the name exactly as the user mentioned it.
- For date filters (DF/DT): return YYYY-MM-DD format.
- If a filter has a default value and the user did not mention it, use the default.
- If a value cannot be determined, omit that field.
- Do not invent values the user did not mention or that have no default.

Respond with a JSON object only. No explanation.
The keys must match the filter field names exactly."""


def _build_user_prompt(
    question: str,
    filters_parsed: list,
    bound_filters: dict,
) -> str:
    filter_lines = []
    for spec in filters_parsed:
        default = spec.default_value if spec.default_value else "none"
        filter_lines.append(f"{spec.field_name} (type: {spec.filter_type}, default: {default})")

    return (
        f"Question: {question}\n\n"
        f"Available filters:\n"
        + "\n".join(filter_lines)
        + "\n\n"
        f"Previous context (already applied):\n"
        f"{json.dumps(bound_filters)}"
    )


def _update_selected_entities(new_filters: dict, selected_entities: dict) -> dict:
    new_entities = {**selected_entities}
    for key in ENTITY_KEYS:
        if key in new_filters:
            new_entities[key.lower()] = new_filters[key]
    return new_entities


async def binder_node(state: AgentState) -> dict:
    if state.get("error"):
        return {}

    existing_filters = state.get("bound_filters", {})
    existing_entities = state.get("selected_entities", {})

    report_id = state.get("resolved_report_id")
    if not report_id:
        return {
            "bound_filters": existing_filters,
            "selected_entities": existing_entities,
        }

    try:
        async with AsyncSessionLocal() as db:
            repo = CatalogRepository(db)
            report = await repo.get_by_id(report_id)

        if not report:
            return {
                "bound_filters": existing_filters,
                "selected_entities": existing_entities,
            }

        if not report.filters_parsed:
            return {
                "bound_filters": existing_filters,
                "selected_entities": existing_entities,
            }

        settings = get_settings()
        today = datetime.date.today()
        llm = ChatAnthropic(
            model="claude-haiku-4-5",
            api_key=settings.anthropic_api_key,
        )
        response = await llm.ainvoke(
            [
                SystemMessage(content=_build_system_prompt(today)),
                HumanMessage(
                    content=_build_user_prompt(
                        state["current_question"],
                        report.filters_parsed,
                        existing_filters,
                    )
                ),
            ]
        )
        llm_extracted = _parse_llm_json(response.content)

        new_filters = {**existing_filters}
        for key, value in llm_extracted.items():
            new_filters[key] = value

        new_entities = _update_selected_entities(new_filters, existing_entities)

        return {
            "bound_filters": new_filters,
            "selected_entities": new_entities,
        }
    except Exception:
        return {
            "bound_filters": existing_filters,
            "selected_entities": existing_entities,
            "error": "Filter extraction failed — using defaults.",
        }
