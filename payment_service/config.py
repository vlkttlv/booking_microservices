from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODE: Literal["DEV", 'TEST', 'PROD']
    LOG_LEVEL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_SECRET_KEY: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:  # настройки будут загружаться из файла .env
        env_file = "payment_service/.env"


settings = Settings()  # содержит значения настроек из файла .env