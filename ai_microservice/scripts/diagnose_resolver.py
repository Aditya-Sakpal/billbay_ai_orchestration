"""Diagnose why resolver returns no matching report."""

from __future__ import annotations

import asyncio
import traceback

from app.agent.nodes.node2_resolver import (
    _embed_question,
    _rerank_candidates,
    _vector_search,
)
from app.config import get_settings


async def main() -> None:
    get_settings.cache_clear()
    question = "Show me sales performance for Karen Ku"
    print("Question:", question)
    try:
        emb = await _embed_question(question)
        print("Embedding dim:", len(emb))
        candidates = await _vector_search(emb, 50)
        print("Candidates:", len(candidates))
        for c in candidates:
            print(f"  {c['id']}: {c['report_name']} sim={c.get('similarity', 0):.3f}")
        if candidates:
            idx = await _rerank_candidates(question, candidates)
            print("Rerank best_index:", idx, candidates[idx]["report_name"])
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
