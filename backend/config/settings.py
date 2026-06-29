from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM
    GMAIL_ADDRESS: Optional[str] = None
    GMAIL_APP_PASSWORD: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "anthropic"

    # Tools
    SERPER_API_KEY: Optional[str] = None
    APOLLO_API_KEY: Optional[str] = None
    HUNTER_API_KEY: Optional[str] = None
    PROXYCURL_API_KEY: Optional[str] = None

    # Mock mode — auto true when keys missing
    MOCK_MODE: bool = True

    # DB — SQLite, no container needed
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # Redis — optional, falls back to in-memory
    REDIS_URL: Optional[str] = None

    # App
    SECRET_KEY: str = "change-me-in-production"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()