from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "live-data-share-and-think"
    database_url: str = "sqlite:///./local.db"
    fixture_path: str = "backend/tests/fixtures/xhs_notes.json"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

