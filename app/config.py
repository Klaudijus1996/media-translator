import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BASE_STORAGE_PATH: str = os.getenv("STORAGE_DIR", "/storage")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    STORAGE_DIR: str = f"{BASE_STORAGE_PATH}/app"
    LOG_DIR: Path = Path(f"{BASE_STORAGE_PATH}/logs")

    class Config:
        case_sensitive = True

settings = Settings()
