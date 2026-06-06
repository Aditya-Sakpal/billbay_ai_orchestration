from langgraph.graph import END, StateGraph

from app.agent.nodes.node1_intent import intent_node
from app.agent.nodes.node2_resolver import resolver_node
from app.agent.nodes.node3_binder import binder_node
from app.agent.nodes.node4_executor import executor_node
from app.agent.nodes.node5_narrator import narrator_node
from app.agent.state import AgentState

builder = StateGraph(AgentState)

builder.add_node("intent", intent_node)
builder.add_node("resolver", resolver_node)
builder.add_node("binder", binder_node)
builder.add_node("executor", executor_node)
builder.add_node("narrator", narrator_node)

builder.set_entry_point("intent")


def route_after_intent(state: AgentState) -> str:
    if state.get("error"):
        return "narrator"
    return "resolver"


builder.add_conditional_edges(
    "intent",
    route_after_intent,
    {"narrator": "narrator", "resolver": "resolver"},
)


def route_after_resolver(state: AgentState) -> str:
    if state.get("error"):
        return "narrator"
    return "binder"


builder.add_conditional_edges(
    "resolver",
    route_after_resolver,
    {"narrator": "narrator", "binder": "binder"},
)

builder.add_edge("binder", "executor")


def route_after_executor(state: AgentState) -> str:
    return "narrator"


builder.add_conditional_edges(
    "executor",
    route_after_executor,
    {"narrator": "narrator"},
)

builder.add_edge("narrator", END)

graph = builder.compile()
