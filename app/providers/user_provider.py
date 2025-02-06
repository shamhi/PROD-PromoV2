from typing import Iterable, AsyncIterable

from httpx import AsyncClient
from redis.asyncio import Redis
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings
from app.database.postgres.session import get_db
from app.database.repositories.user import UserRepository
from app.interactors.antifraud import AntifraudInteractor
from app.interactors.caching import CacheAccessTokenInteractor, CacheAntifraudInteractor
from app.interactors.auth import (
    SignUpUserInteractor,
    SignInUserInteractor,
    OAuth2PasswordBearerUserInteractor,
)
from app.interactors.user import (
    GetUserProfileInteractor,
    PatchUserByIdInteractor,
    GetUserPromoFeedInteractor,
    GetUserPromoByIdInteractor,
    AddLikeToPromoInteractor,
    DeleteLikeToPromoInteractor,
    AddCommentToPromoInteractor,
    GetPromoCommentsInteractor,
    GetPromoCommentByIdInteractor,
    EditUserCommentByIdInteractor,
    DeleteUserCommentByIdInteractor,
    UserActivatePromoByIdInteractor,
    GetPromoActivationsHistoryInteractor,
)


class UserProvider(Provider):
    scope = Scope.REQUEST

    def __init__(self, config: Settings):
        super().__init__()
        self.config = config

    @provide
    async def get_user_repository(self, engine: AsyncEngine) -> AsyncIterable[UserRepository]:
        async for db_session in get_db(engine):
            yield UserRepository(db_session)

    @provide
    def get_sign_up_interactor(self, repo: UserRepository) -> Iterable[SignUpUserInteractor]:
        yield SignUpUserInteractor(repo)

    @provide
    def get_sign_in_interactor(self, repo: UserRepository) -> Iterable[SignInUserInteractor]:
        yield SignInUserInteractor(repo)

    @provide
    def get_oauth_password_bearer_interactor(
        self,
    ) -> Iterable[OAuth2PasswordBearerUserInteractor]:
        yield OAuth2PasswordBearerUserInteractor()

    @provide
    def get_cache_access_token_interactor(self, redis: Redis) -> Iterable[CacheAccessTokenInteractor]:
        yield CacheAccessTokenInteractor(redis, self.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    @provide
    def get_user_profile_interactor(self, repo: UserRepository) -> Iterable[GetUserProfileInteractor]:
        yield GetUserProfileInteractor(repo)

    @provide
    def get_patch_user_interactor(self, repo: UserRepository) -> Iterable[PatchUserByIdInteractor]:
        yield PatchUserByIdInteractor(repo)

    @provide
    def get_user_promo_feed_interactor(self, repo: UserRepository) -> Iterable[GetUserPromoFeedInteractor]:
        yield GetUserPromoFeedInteractor(repo)

    @provide
    def get_user_promo_by_id_interactor(self, repo: UserRepository) -> Iterable[GetUserPromoByIdInteractor]:
        yield GetUserPromoByIdInteractor(repo)

    @provide
    def get_add_like_to_promo_interactor(self, repo: UserRepository) -> Iterable[AddLikeToPromoInteractor]:
        yield AddLikeToPromoInteractor(repo)

    @provide
    def get_delete_like_to_promo_interactor(self, repo: UserRepository) -> Iterable[DeleteLikeToPromoInteractor]:
        yield DeleteLikeToPromoInteractor(repo)

    @provide
    def get_add_comment_to_promo_interactor(self, repo: UserRepository) -> Iterable[AddCommentToPromoInteractor]:
        yield AddCommentToPromoInteractor(repo)

    @provide
    def get_user_promo_comments_interactor(self, repo: UserRepository) -> Iterable[GetPromoCommentsInteractor]:
        yield GetPromoCommentsInteractor(repo)

    @provide
    def get_promo_comment_by_id_interactor(self, repo: UserRepository) -> Iterable[GetPromoCommentByIdInteractor]:
        yield GetPromoCommentByIdInteractor(repo)

    @provide
    def get_edit_user_comment_by_id_interactor(self, repo: UserRepository) -> Iterable[EditUserCommentByIdInteractor]:
        yield EditUserCommentByIdInteractor(repo)

    @provide
    def get_delete_user_comment_by_id_interactor(
        self, repo: UserRepository
    ) -> Iterable[DeleteUserCommentByIdInteractor]:
        yield DeleteUserCommentByIdInteractor(repo)

    @provide
    def get_user_activate_promo_by_id_interactor(
        self, repo: UserRepository
    ) -> Iterable[UserActivatePromoByIdInteractor]:
        yield UserActivatePromoByIdInteractor(repo)

    @provide
    def get_antifraud_interactor(self, http_client: AsyncClient) -> Iterable[AntifraudInteractor]:
        yield AntifraudInteractor(http_client)

    @provide
    def get_caching_antifraud_interactor(self, redis: Redis) -> Iterable[CacheAntifraudInteractor]:
        yield CacheAntifraudInteractor(redis)

    @provide
    def get_promo_activations_history_interactor(
        self, repo: UserRepository
    ) -> Iterable[GetPromoActivationsHistoryInteractor]:
        yield GetPromoActivationsHistoryInteractor(repo)
