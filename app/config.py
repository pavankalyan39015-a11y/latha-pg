from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    API_TITLE: str = "Latha PG for Gents Management API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = (
        "Complete Management System for Latha PG for Gents (ಲತಾ ಪಿಜಿ - ಪುರುಷರಿಗೆ). "
        "Comfortable, safe, and affordable 2, 3, and 4 sharing accommodation with attached bathrooms, "
        "high-speed Wi-Fi, 24/7 CCTV surveillance, washing machine, and power backup. Contact: 9353439703 | 9019870803."
    )
    DATABASE_URL: str = "sqlite:///./pg_management.db"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
