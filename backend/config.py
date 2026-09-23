"""Application configuration for CareerTwin AI."""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False, extra='ignore')

    app_name: str = 'CareerTwin AI'
    app_env: str = 'development'
    secret_key: str = Field(default='change-this-secret-in-production')
    access_token_expire_minutes: int = 1440
    database_url: str = 'sqlite+aiosqlite:///./data/careertwin.db'

    # Google Gemini API. Keep this key only in .env / deployment secrets.
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.5-flash-lite'
    gemini_timeout_seconds: int = 90

    allowed_origins: str = 'http://localhost:5173,http://localhost:3000'
    max_upload_size_mb: int = 5
    upload_folder: str = 'data/uploads'

    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(',') if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
