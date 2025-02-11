from collections.abc import Iterable

from dishka import Provider

from app.ioc.providers import (
    AntifraudProvider,
    ConfigProvider,
    InteractorProvider,
    PostgresProvider,
    RedisProvider,
    RepositoryProvider,
    SecurityProvider,
)


def get_providers() -> Iterable[Provider]:
    return (
        ConfigProvider(),
        SecurityProvider(),
        InteractorProvider(),
        RepositoryProvider(),
        PostgresProvider(),
        RedisProvider(),
        AntifraudProvider(),
    )
