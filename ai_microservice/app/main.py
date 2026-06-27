import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, health

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="vlang", version="0.1.0")


@app.on_event("startup")
async def log_startup_config() -> None:
    get_settings.cache_clear()
    settings = get_settings()
    logging.getLogger("vlang.pipeline").setLevel(logging.INFO)
    logger.info(
        "DATA_SOURCE_MODE=%s dashboard_api=%s cookie_set=%s",
        settings.data_source_mode,
        settings.dashboard_base_url,
        bool(settings.dashboard_session_cookie),
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
