import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session_state(session: AsyncSession, session_id: str) -> dict[str, Any] | None:
    result = await session.execute(
        text("SELECT state FROM session_state WHERE session_id = :session_id"),
        {"session_id": session_id},
    )
    row = result.mappings().first()
    if row is None:
        return None
    state = row["state"]
    if isinstance(state, str):
        return json.loads(state)
    return state


async def upsert_session_state(
    session: AsyncSession,
    session_id: str,
    state: dict[str, Any],
) -> None:
    await session.execute(
        text(
            """
            INSERT INTO session_state (session_id, state, updated_at)
            VALUES (:session_id, :state::jsonb, NOW())
            ON CONFLICT (session_id)
            DO UPDATE SET state = EXCLUDED.state, updated_at = NOW()
            """
        ),
        {"session_id": session_id, "state": json.dumps(state)},
    )
    await session.commit()


async def delete_session_state(session: AsyncSession, session_id: str) -> bool:
    result = await session.execute(
        text("DELETE FROM session_state WHERE session_id = :session_id"),
        {"session_id": session_id},
    )
    await session.commit()
    return result.rowcount > 0
