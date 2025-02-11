from dishka import Provider, Scope, from_context, provide

from app.core.config import (
    AntifraudConfig,
    Config,
    PostgresConfig,
    RedisConfig,
    SecurityConfig,
    create_config,
)


class ConfigProvider(Provider):
    scope = Scope.APP
    config = from_context(provides=Config)

    @provide
    def get_config(self) -> Config:
        return create_config()

    @provide
    def get_postgres_config(self, config: Config) -> PostgresConfig:
        return config.postgres_config

    @provide
    def get_redis_config(self, config: Config) -> RedisConfig:
        return config.redis_config

    @provide
    def get_antifraud_config(self, config: Config) -> AntifraudConfig:
        return config.antifraud_config

    @provide
    def get_auth_token_config(self, config: Config) -> SecurityConfig:
        return config.auth_token_config
