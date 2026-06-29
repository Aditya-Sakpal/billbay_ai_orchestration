"""Structured debug logging for the LangGraph BI pipeline."""

from __future__ import annotations

import logging
import traceback

logger = logging.getLogger("vlang.pipeline")


def log_stage(stage: str, **fields: object) -> None:
    parts = [f"{key}={value!r}" for key, value in fields.items()]
    logger.info("[%s] %s", stage, " ".join(parts))


def log_exception(stage: str, exc: BaseException, **fields: object) -> None:
    """Log exception with full traceback (filename, line number, stack)."""
    parts = [f"{key}={value!r}" for key, value in fields.items()]
    prefix = f"[{stage}] {' '.join(parts)}".strip()
    logger.error("%s %s: %s", prefix, type(exc).__name__, exc)
    logger.error("%s traceback:\n%s", prefix, traceback.format_exc())
