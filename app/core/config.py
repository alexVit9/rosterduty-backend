from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/rosterduty"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@rosterduty.com"
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587

    # Comma-separated origins, e.g. "https://rosterduty.com,https://www.rosterduty.com"
    CORS_ORIGINS_STR: str = "*"
    FRONTEND_URL: str = "https://rosterduty.com"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        if self.CORS_ORIGINS_STR == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS_STR.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
