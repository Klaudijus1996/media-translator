import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATA_DIR: str = os.getenv("DATA_DIR", "/data")
    LOG_DIR: Path = Path(f"{DATA_DIR}/logs")

    class Config:
        case_sensitive = True

settings = Settings()
# Ensure logs dir exists
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
