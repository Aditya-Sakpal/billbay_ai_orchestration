from typing import TypedDict


class AgentIdentity(TypedDict):
    session_id: str
    user_id: int
    access_level: int


class AgentState(AgentIdentity, total=False):
    messages: list[dict]
    current_question: str
    intent_domain: str | None
    resolved_report_id: int | None
    resolved_report_name: str | None
    bound_filters: dict
    selected_entities: dict
    query_result: list[dict]
    answer: str
    error: str | None
