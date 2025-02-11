from dataclasses import dataclass
from os import getenv
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class PostgresConfig:
    POSTGRES_CONN: str | None
    POSTGRES_JDBC_URL: str | None
    POSTGRES_USERNAME: str | None
    POSTGRES_PASSWORD: str | None
    POSTGRES_HOST: str | None
    POSTGRES_PORT: int | None
    POSTGRES_DATABASE: str | None

    @staticmethod
    def from_env() -> "PostgresConfig":
        conn = getenv("POSTGRES_CONN")
        jdbc = getenv("POSTGRES_JDBC_URL")
        username = getenv("POSTGRES_USERNAME")
        password = getenv("POSTGRES_PASSWORD")
        host = getenv("POSTGRES_HOST")
        port = getenv("POSTGRES_PORT")
        database = getenv("POSTGRES_DATABASE")

        return PostgresConfig(
            POSTGRES_CONN=conn,
            POSTGRES_JDBC_URL=jdbc,
            POSTGRES_USERNAME=username,
            POSTGRES_PASSWORD=password,
            POSTGRES_HOST=host,
            POSTGRES_PORT=port,
            POSTGRES_DATABASE=database,
        )


@dataclass(frozen=True)
class ServerConfig:
    SERVER_ADDRESS: str
    SERVER_PORT: int | None

    @staticmethod
    def from_env() -> "ServerConfig":
        address = getenv("SERVER_ADDRESS", "0.0.0.0:8080")
        port = getenv("SERVER_PORT", 8080)

        return ServerConfig(SERVER_ADDRESS=address, SERVER_PORT=port)


@dataclass(frozen=True)
class RedisConfig:
    REDIS_HOST: str
    REDIS_PORT: int

    @staticmethod
    def from_env() -> "RedisConfig":
        host = getenv("REDIS_HOST", "localhost")
        port = getenv("REDIS_PORT", 6379)

        return RedisConfig(REDIS_HOST=host, REDIS_PORT=port)


@dataclass(frozen=True)
class SecurityConfig:
    RANDOM_SECRET: str
    ALGORITH: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @staticmethod
    def from_env() -> "SecurityConfig":
        secret = getenv("RANDOM_SECRET")
        algorithm = getenv("ALGORITH", "HS256")
        expire_minutes = getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)

        return SecurityConfig(RANDOM_SECRET=secret, ALGORITH=algorithm, ACCESS_TOKEN_EXPIRE_MINUTES=expire_minutes)


@dataclass(frozen=True)
class AntifraudConfig:
    ANTIFRAUD_ADDRESS: str

    @staticmethod
    def from_env() -> "AntifraudConfig":
        address = getenv("ANTIFRAUD_ADDRESS", "localhost:9090")

        return AntifraudConfig(ANTIFRAUD_ADDRESS=address)


@dataclass(frozen=True)
class Config:
    postgres_config: PostgresConfig
    server_config: ServerConfig
    redis_config: RedisConfig
    security_config: SecurityConfig
    antifraud_config: AntifraudConfig


def create_config() -> Config:
    return Config(
        postgres_config=PostgresConfig.from_env(),
        server_config=ServerConfig.from_env(),
        redis_config=RedisConfig.from_env(),
        security_config=SecurityConfig.from_env(),
        antifraud_config=AntifraudConfig.from_env(),
    )
