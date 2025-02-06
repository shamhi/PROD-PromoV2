from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    SERVER_ADDRESS: str = "0.0.0.0:8080"
    SERVER_PORT: Optional[int] = 8080

    POSTGRES_CONN: Optional[str] = None
    POSTGRES_JDBC_URL: Optional[str] = None

    POSTGRES_USERNAME: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_DATABASE: Optional[str] = None

    REDIS_HOST: Optional[str] = "localhost"
    REDIS_PORT: Optional[int] = 6379

    ANTIFRAUD_ADDRESS: Optional[str] = "localhost:9090"

    RANDOM_SECRET: str
    ALGORITH: Optional[str] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = 60


Config = Settings()
