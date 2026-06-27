import logging
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load ai_microservice env and make its app package importable before other imports.
REPO_ROOT = Path(__file__).resolve().parent.parent
AI_MS_ROOT = REPO_ROOT / "ai_microservice"
load_dotenv(AI_MS_ROOT / ".env")
sys.path.insert(0, str(AI_MS_ROOT))

from app.agent.graph import graph  # noqa: E402

logger = logging.getLogger(__name__)

app = FastAPI(title="Chatbot B", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session state keyed by ChatRequest.user_id (supports multi-turn REST chat).
_sessions: dict[str, dict] = {}


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user")
    message: str = Field(..., description="User message to the chatbot")
    access_level: int = Field(
        default=50,
        ge=0,
        le=100,
        description="BillBay access level for report permissions (default 50)",
    )


class ChatResponse(BaseModel):
    status: str = Field(..., description="Response status: ok or error")
    reply: str = Field(..., description="Chatbot reply text")


def _parse_user_id(user_id: str) -> int:
    """Graph expects numeric user_id for VCORBI row scoping; default to demo user 42."""
    try:
        return int(user_id)
    except ValueError:
        logger.info("Non-numeric user_id %r — using demo user_id=42", user_id)
        return 42


def _get_session(user_id: str, access_level: int) -> dict:
    if user_id not in _sessions:
        _sessions[user_id] = {
            "session_id": str(uuid.uuid4()),
            "user_id": _parse_user_id(user_id),
            "access_level": access_level,
            "messages": [],
            "bound_filters": {},
            "selected_entities": {},
        }
    else:
        _sessions[user_id]["access_level"] = access_level
    return _sessions[user_id]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "chatbot-b"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    state = _get_session(request.user_id, request.access_level)
    state["messages"].append({"role": "user", "content": request.message})
    state["current_question"] = request.message
    state.pop("error", None)
    state["answer"] = ""

    try:
        result = await graph.ainvoke(state)
        state.update(result)
    except Exception:
        logger.exception("Graph invocation failed for user_id=%s", request.user_id)
        return ChatResponse(
            status="error",
            reply="Something went wrong while processing your question. Please try again.",
        )

    answer = state.get("answer") or "I could not generate a response."
    if state.get("error"):
        return ChatResponse(status="error", reply=answer)

    return ChatResponse(status="ok", reply=answer)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
