from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "live-data-share-and-think"
    database_url: str = "sqlite:///./local.db"
    fixture_path: str = "backend/tests/fixtures/xhs_notes.json"
    generation_provider: Literal["auto", "template", "deepseek"] = "auto"
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"
    collection_proxy_url: str | None = None
    collection_proxy_token: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
