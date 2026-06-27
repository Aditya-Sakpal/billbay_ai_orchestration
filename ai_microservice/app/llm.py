"""Shared Anthropic client factory for LangGraph nodes."""

from langchain_anthropic import ChatAnthropic

from app.config import get_settings


def get_chat_anthropic(model: str) -> ChatAnthropic:
    """
    Build ChatAnthropic using either:
    - ANTHROPIC_API_KEY (sk-ant-... from console.anthropic.com), or
    - ANTHROPIC_OAUTH_TOKEN (Bearer token for org / Claude OAuth flows)
    """
    settings = get_settings()

    if settings.anthropic_oauth_token:
        return ChatAnthropic(
            model=model,
            api_key=settings.anthropic_oauth_token,
            default_headers={
                "Authorization": f"Bearer {settings.anthropic_oauth_token}",
                "anthropic-version": "2023-06-01",
            },
        )

    return ChatAnthropic(model=model, api_key=settings.anthropic_api_key)
