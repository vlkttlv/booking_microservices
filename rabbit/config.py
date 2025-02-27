from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USE: str
    SMTP_PASS: str
    
    RABBITMQ_URL: str
    QUEUE_NAME: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int


    class Config:
        env_file = "rabbit/.env"


settings = Settings()