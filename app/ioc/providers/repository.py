from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine

from app.database.postgres.session import get_db
from app.database.repositories.business import BusinessCompanyRepository
from app.database.repositories.user import UserRepository


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_business_company_repository(self, engine: AsyncEngine) -> AsyncIterable[BusinessCompanyRepository]:
        async for db_session in get_db(engine):
            yield BusinessCompanyRepository(db_session)

    @provide
    async def get_user_repository(self, engine: AsyncEngine) -> AsyncIterable[UserRepository]:
        async for db_session in get_db(engine):
            yield UserRepository(db_session)
