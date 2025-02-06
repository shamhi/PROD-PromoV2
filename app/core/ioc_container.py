from dishka import make_async_container

from app.core.config import Config
from app.providers import InitProvider, UserProvider, BusinessCompanyProvider

container = make_async_container(
    InitProvider(Config),
    UserProvider(Config),
    BusinessCompanyProvider(Config),
)
