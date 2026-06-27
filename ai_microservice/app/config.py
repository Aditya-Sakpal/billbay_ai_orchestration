from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    vcorbi_url: str
    anthropic_api_key: str = ""
    anthropic_oauth_token: str = ""
    anthropic_api_key_id: str = ""
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_host: str
    catalog_csv_path: str = "data/cs_dashboard_menu.csv"
    vcorbi_mode: str = "mock"
    # vcorbi_mock | dashboard_api
    data_source_mode: str = "vcorbi_mock"
    dashboard_base_url: str = "https://csportal.billbay.co"
    dashboard_api_url: str = ""
    dashboard_session_cookie: str = ""
    dashboard_referer: str = "https://csportal.billbay.co/dashboard.php"
    dashboard_api_method: str = "POST"
    dashboard_api_timeout: int = 30
    embedding_provider: str = "openai"
    local_embedding_model: str = "all-MiniLM-L6-v2"
    openai_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
