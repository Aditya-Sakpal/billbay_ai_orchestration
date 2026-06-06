import logging
import uuid

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.agent.graph import graph

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/chat")
async def chat_ws(
    websocket: WebSocket,
    user_id: int = Query(...),
    access_level: int = Query(...),
) -> None:
    await websocket.accept()
    session_id = str(uuid.uuid4())
    state: dict = {
        "session_id": session_id,
        "user_id": user_id,
        "access_level": access_level,
        "messages": [],
        "bound_filters": {},
        "selected_entities": {},
    }

    try:
        while True:
            user_text = await websocket.receive_text()
            state["messages"].append({"role": "user", "content": user_text})
            state["current_question"] = user_text

            try:
                result = await graph.ainvoke(state)
                state.update(result)
            except Exception:
                logger.exception("Graph invocation failed for session %s", session_id)
                await websocket.send_json(
                    {
                        "answer": "Something went wrong. Please try again.",
                        "error": True,
                        "report": state.get("resolved_report_name"),
                        "filters": state.get("bound_filters", {}),
                        "session_id": session_id,
                    }
                )
                continue

            await websocket.send_json(
                {
                    "answer": state.get("answer", ""),
                    "report": state.get("resolved_report_name"),
                    "filters": state.get("bound_filters", {}),
                    "session_id": session_id,
                }
            )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: session_id=%s", session_id)
