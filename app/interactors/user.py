from typing import List, Tuple

from app.core.exceptions import EntityAccessDeniedError
from app.core.security import Security
from app.database.repositories.user import UserRepository
from app.interactors.antifraud import AntifraudInteractor
from app.interactors.caching import CacheAntifraudInteractor
from app.schemas.common import CommentId, CommentText, PromoId, UserId
from app.schemas.user import Comment, PromoForUser, User, UserPatch
from app.utils.serializer import (
    serialize_comment,
    serialize_promo_for_user,
    serialize_user,
)


class GetUserProfileInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_id: str) -> User:
        user_orm = await self.user_repository.get_user_by_id(user_id=user_id)

        user = serialize_user(user_orm)

        return user


class PatchUserByIdInteractor:
    def __init__(self, user_repository: UserRepository, security: Security):
        self.user_repository = user_repository
        self.security = security

    async def __call__(self, user_id: str, user_patch: UserPatch) -> User:
        user_orm = await self.user_repository.patch_user_by_id(user_id=user_id, user_patch=user_patch, security=self.security)

        user = serialize_user(user_orm)

        return user


class GetUserPromoFeedInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(
        self, user_id: UserId, category: str, active: bool, limit: int, offset: int
    ) -> tuple[int, list[PromoForUser]]:
        total_count, promos = await self.user_repository.get_promos_for_user(
            user_id=user_id,
            category=category,
            active=active,
            limit=limit,
            offset=offset,
        )

        promos_for_user = [serialize_promo_for_user(promo, user_id) for promo in promos]

        return total_count, promos_for_user


class GetUserPromoByIdInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_id: UserId, promo_id: PromoId) -> PromoForUser:
        promo = await self.user_repository.get_promo_for_user_by_id(promo_id=promo_id)

        promo_for_user = serialize_promo_for_user(promo, user_id)

        return promo_for_user


class AddLikeToPromoInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_id: UserId, promo_id: PromoId) -> None:
        await self.user_repository.add_like_to_promo(user_id=user_id, promo_id=promo_id)


class DeleteLikeToPromoInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_id: UserId, promo_id: PromoId) -> None:
        await self.user_repository.delete_like_to_promo(user_id=user_id, promo_id=promo_id)


class AddCommentToPromoInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_id: UserId, promo_id: PromoId, comment_text: CommentText) -> Comment:
        comment_orm = await self.user_repository.add_comment_to_promo(
            user_id=user_id, promo_id=promo_id, comment_text=comment_text
        )

        comment = serialize_comment(comment_orm)

        return comment


class GetPromoCommentsInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, promo_id: PromoId, limit: int, offset: int) -> tuple[int, list[Comment]]:
        total_count, comments_orm = await self.user_repository.get_promo_comments(promo_id=promo_id, limit=limit, offset=offset)

        comments = [serialize_comment(comment_orm) for comment_orm in comments_orm]

        return total_count, comments


class GetPromoCommentByIdInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, promo_id: PromoId, comment_id: CommentId) -> Comment:
        comment_orm = await self.user_repository.get_promo_comment_by_id(promo_id=promo_id, comment_id=comment_id)

        comment = serialize_comment(comment_orm)

        return comment


class EditUserCommentByIdInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(
        self,
        user_id: UserId,
        promo_id: PromoId,
        comment_id: CommentId,
        comment_text: CommentText,
    ) -> Comment:
        comment_orm = await self.user_repository.edit_user_comment_by_id(
            user_id=user_id,
            promo_id=promo_id,
            comment_id=comment_id,
            comment_text=comment_text,
        )

        comment = serialize_comment(comment_orm)

        return comment


class DeleteUserCommentByIdInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(
        self,
        user_id: UserId,
        promo_id: PromoId,
        comment_id: CommentId,
    ) -> None:
        await self.user_repository.delete_user_comment_by_id(user_id=user_id, promo_id=promo_id, comment_id=comment_id)


class UserActivatePromoByIdInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(
        self,
        user_id: UserId,
        promo_id: PromoId,
        antifraud_interactor: AntifraudInteractor,
        caching_interactor: CacheAntifraudInteractor,
    ) -> str:
        cached_response = await caching_interactor.get_cached_response(user_id=user_id)

        if cached_response:
            if not cached_response.ok:
                raise EntityAccessDeniedError
        else:
            user = await self.user_repository.get_user_by_id(user_id=user_id)

            antifraud_response = await antifraud_interactor(user_email=user.email, promo_id=promo_id)

            if not antifraud_response.ok:
                raise EntityAccessDeniedError

            await caching_interactor.save_response(user_id=user_id, antifraud_response=antifraud_response)

        promo_code = await self.user_repository.activate_promo_by_id(user_id=user_id, promo_id=promo_id)

        return promo_code


class GetPromoActivationsHistoryInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_id: UserId, limit: int, offset: int) -> tuple[int, list[PromoForUser]]:
        (
            total_count,
            promos,
        ) = await self.user_repository.get_user_promo_activations_history(user_id=user_id, limit=limit, offset=offset)

        promos_for_user = [serialize_promo_for_user(promo, user_id) for promo in promos]

        return total_count, promos_for_user
