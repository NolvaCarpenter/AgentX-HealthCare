from pydantic_settings import BaseSettings
from pydantic import SecretStr
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Authentication
    AUTH_SECRET: Optional[SecretStr] = None
    BASE_URL: str = "http://127.0.0.1:1500"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
