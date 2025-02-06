from typing import Iterable, AsyncIterable

from redis.asyncio import Redis
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings
from app.database.postgres.session import get_db
from app.database.repositories.business import BusinessCompanyRepository
from app.interactors.caching import CacheAccessTokenInteractor
from app.interactors.auth import (
    SignUpBusinessCompanyInteractor,
    SignInBusinessCompanyInteractor,
    OAuth2PasswordBearerCompanyInteractor,
)
from app.interactors.business import (
    CreateNewPromoInteractor,
    GetPromosListInteractor,
    GetPromoByIdInteractor,
    PatchPromoByIdInteractor,
    GetPromoStatByIdInteractor,
)


class BusinessCompanyProvider(Provider):
    scope = Scope.REQUEST

    def __init__(self, config: Settings):
        super().__init__()
        self.config = config

    @provide
    async def get_business_company_repository(self, engine: AsyncEngine) -> AsyncIterable[BusinessCompanyRepository]:
        async for db_session in get_db(engine):
            yield BusinessCompanyRepository(db_session)

    @provide
    def get_sign_up_interactor(self, repo: BusinessCompanyRepository) -> Iterable[SignUpBusinessCompanyInteractor]:
        yield SignUpBusinessCompanyInteractor(repo)

    @provide
    def get_sign_in_interactor(self, repo: BusinessCompanyRepository) -> Iterable[SignInBusinessCompanyInteractor]:
        yield SignInBusinessCompanyInteractor(repo)

    @provide
    def get_oauth_password_bearer_interactor(
        self,
    ) -> Iterable[OAuth2PasswordBearerCompanyInteractor]:
        yield OAuth2PasswordBearerCompanyInteractor()

    @provide
    def get_cache_access_token_interactor(self, redis: Redis) -> Iterable[CacheAccessTokenInteractor]:
        yield CacheAccessTokenInteractor(redis, self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    @provide
    def get_create_new_promo_interactor(self, repo: BusinessCompanyRepository) -> Iterable[CreateNewPromoInteractor]:
        yield CreateNewPromoInteractor(repo)

    @provide
    def get_promos_list_interactor(self, repo: BusinessCompanyRepository) -> Iterable[GetPromosListInteractor]:
        yield GetPromosListInteractor(repo)

    @provide
    def get_promo_by_id_interactor(self, repo: BusinessCompanyRepository) -> Iterable[GetPromoByIdInteractor]:
        yield GetPromoByIdInteractor(repo)

    @provide
    def get_patch_promo_by_id_interactor(self, repo: BusinessCompanyRepository) -> Iterable[PatchPromoByIdInteractor]:
        yield PatchPromoByIdInteractor(repo)

    @provide
    def get_promo_stat_by_id_interactor(self, repo: BusinessCompanyRepository) -> Iterable[GetPromoStatByIdInteractor]:
        yield GetPromoStatByIdInteractor(repo)
