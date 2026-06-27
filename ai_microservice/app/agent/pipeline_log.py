"""Structured debug logging for the LangGraph BI pipeline."""

from __future__ import annotations

import logging

logger = logging.getLogger("vlang.pipeline")


def log_stage(stage: str, **fields: object) -> None:
    parts = [f"{key}={value!r}" for key, value in fields.items()]
    logger.info("[%s] %s", stage, " ".join(parts))
