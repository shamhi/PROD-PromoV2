from collections.abc import Iterable
from datetime import date
from typing import Tuple

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    EntityAccessDeniedError,
    EntityNotFoundError,
    EntityUnauthorizedError,
)
from app.core.security import Security
from app.database.postgres.models import (
    CommentModel,
    PromoModel,
    PromoTargetModel,
    PromoUniqueValueModel,
    UserModel,
    UserPromoActivationModel,
)
from app.schemas.common import CommentId, CommentText, Email, PromoId, UserId
from app.schemas.enums import PromoModeEnum
from app.schemas.user import UserPatch, UserRegister
from app.utils.time import get_comment_date


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_new_user(self, user: UserRegister, security: Security) -> UserModel:
        hashed_password = security.get_password_hash(user.password)
        new_user = UserModel(
            name=user.name,
            surname=user.surname,
            email=user.email,
            password=hashed_password,
            avatar_url=str(user.avatar_url) if user.avatar_url else None,
            age=user.other.age,
            country=user.other.country,
        )

        self.db_session.add(new_user)
        await self.db_session.commit()
        await self.db_session.refresh(new_user)

        return new_user

    async def get_user_by_email(self, email: Email) -> UserModel:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.db_session.execute(query)

        return result.scalars().one_or_none()

    async def get_user_by_id(self, user_id: UserId) -> UserModel:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.db_session.execute(query)

        return result.scalars().one_or_none()

    async def patch_user_by_id(self, user_id: UserId, user_patch: UserPatch, security: Security) -> UserModel:
        query = select(UserModel).where(UserModel.id == user_id)

        result = await self.db_session.execute(query)
        user = result.scalars().one_or_none()

        if not user:
            raise EntityUnauthorizedError

        if user_patch.name:
            user.name = user_patch.name
        if user_patch.surname:
            user.surname = user_patch.surname
        if user_patch.avatar_url:
            user.avatar_url = str(user_patch.avatar_url)
        if user_patch.password:
            user.password = security.get_password_hash(user_patch.password)

        await self.db_session.commit()
        await self.db_session.refresh(user)

        return user

    async def get_promos_for_user(
        self, user_id: UserId, category: str, active: bool, limit: int, offset: int
    ) -> tuple[int, Iterable[PromoModel]]:
        query = select(PromoModel).options(
            selectinload(PromoModel.liked_by_users),
            selectinload(PromoModel.company),
            selectinload(PromoModel.comments),
            selectinload(PromoModel.activations),
            selectinload(PromoModel.unique_values),
        )

        if active is not None:
            active_cond = self.get_user_promo_active_condition()
            query = query.where(active_cond) if active else query.where(~active_cond)

        if category:
            category_lower = category.lower()
            unnest_subquery = (
                select(func.lower(func.unnest(PromoTargetModel.categories)))
                .where(PromoTargetModel.promo_id == PromoModel.id)
                .correlate(PromoTargetModel)
            )

            query = query.outerjoin(PromoTargetModel, PromoTargetModel.promo_id == PromoModel.id).filter(
                func.lower(category_lower).in_(unnest_subquery.scalar_subquery())
            )

        user_data = await self.get_user_by_id(user_id)

        if not user_data:
            raise EntityUnauthorizedError

        user_age, user_country = user_data.age, user_data.country

        user_target_subquery = self.get_user_promo_target_query(user_age, user_country)
        query = query.where(or_(~PromoModel.targets.any(), PromoModel.id.in_(user_target_subquery)))

        total_count_query = query.with_only_columns(func.count()).order_by(None)
        total_count = (await self.db_session.execute(total_count_query)).scalar()

        query = query.order_by(PromoModel.created_at.desc()).limit(limit).offset(offset)

        result = await self.db_session.execute(query)
        promos = result.scalars().all()

        return total_count, promos

    async def get_promo_for_user_by_id(self, promo_id: PromoId) -> PromoModel:
        query = (
            select(PromoModel)
            .where(PromoModel.id == promo_id)
            .options(
                selectinload(PromoModel.liked_by_users),
                selectinload(PromoModel.company),
                selectinload(PromoModel.comments),
                selectinload(PromoModel.activations),
                selectinload(PromoModel.unique_values),
            )
        )

        result = await self.db_session.execute(query)
        promo = result.scalars().one_or_none()

        if not promo:
            raise EntityNotFoundError("Промокод не найден.")

        return promo

    async def add_like_to_promo(self, user_id: UserId, promo_id: PromoId) -> None:
        user_query = select(UserModel).where(UserModel.id == user_id).options(selectinload(UserModel.liked_promos))
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalars().one_or_none()

        if not user:
            raise EntityUnauthorizedError

        promo_query = select(PromoModel).where(PromoModel.id == promo_id).options(selectinload(PromoModel.liked_by_users))
        promo_result = await self.db_session.execute(promo_query)
        promo = promo_result.scalars().one_or_none()

        if not promo:
            raise EntityNotFoundError("Промокод не найден.")

        if promo not in user.liked_promos:
            user.liked_promos.append(promo)
            await self.db_session.commit()

    async def delete_like_to_promo(self, user_id: UserId, promo_id: PromoId) -> None:
        user_query = select(UserModel).where(UserModel.id == user_id).options(selectinload(UserModel.liked_promos))
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalars().one_or_none()

        if not user:
            raise EntityUnauthorizedError

        promo_query = select(PromoModel).where(PromoModel.id == promo_id).options(selectinload(PromoModel.liked_by_users))
        promo_result = await self.db_session.execute(promo_query)
        promo = promo_result.scalars().one_or_none()

        if not promo:
            raise EntityNotFoundError("Промокод не найден.")

        if promo in user.liked_promos:
            user.liked_promos.remove(promo)
            await self.db_session.commit()

    async def add_comment_to_promo(self, user_id: UserId, promo_id: PromoId, comment_text: CommentText) -> CommentModel:
        promo_query = select(PromoModel).where(PromoModel.id == promo_id)
        promo_result = await self.db_session.execute(promo_query)
        promo = promo_result.scalars().one_or_none()

        if not promo:
            raise EntityNotFoundError("Промокод не найден.")

        new_comment = CommentModel(
            text=comment_text,
            date=get_comment_date(),
            author_id=user_id,
            promo_id=promo_id,
        )

        self.db_session.add(new_comment)
        await self.db_session.commit()
        await self.db_session.refresh(new_comment)

        query = select(CommentModel).where(CommentModel.id == new_comment.id).options(selectinload(CommentModel.author))

        result = await self.db_session.execute(query)
        new_comment = result.scalars().one_or_none()

        return new_comment

    async def get_promo_comments(self, promo_id: PromoId, limit: int, offset: int) -> tuple[int, Iterable[CommentModel]]:
        query = select(CommentModel).where(CommentModel.promo_id == promo_id).options(selectinload(CommentModel.author))

        total_count_query = query.with_only_columns(func.count()).order_by(None)
        total_count = (await self.db_session.execute(total_count_query)).scalar()

        query = query.order_by(CommentModel.date.desc()).limit(limit).offset(offset)

        result = await self.db_session.execute(query)
        comments = result.scalars().all()

        return total_count, comments

    async def get_promo_comment_by_id(self, promo_id: PromoId, comment_id: CommentId) -> CommentModel:
        query = (
            select(CommentModel)
            .where(and_(CommentModel.id == comment_id, CommentModel.promo_id == promo_id))
            .options(selectinload(CommentModel.author), selectinload(CommentModel.promo))
        )

        result = await self.db_session.execute(query)
        comment = result.scalars().one_or_none()

        if not comment or not comment.promo:
            raise EntityNotFoundError("Такого промокода или комментария не существует.")

        return comment

    async def edit_user_comment_by_id(
        self,
        user_id: UserId,
        promo_id: PromoId,
        comment_id: CommentId,
        comment_text: CommentText,
    ) -> CommentModel:
        query = (
            select(CommentModel)
            .where(and_(CommentModel.id == comment_id, CommentModel.promo_id == promo_id))
            .options(selectinload(CommentModel.author), selectinload(CommentModel.promo))
        )

        result = await self.db_session.execute(query)
        comment = result.scalars().one_or_none()

        if not comment or not comment.promo:
            raise EntityNotFoundError("Такого промокода или комментария не существует.")

        if str(comment.author_id) != str(user_id):
            raise EntityAccessDeniedError("Комментарий не принадлежит пользователю.")

        comment.text = comment_text

        await self.db_session.commit()
        await self.db_session.refresh(comment)

        return comment

    async def delete_user_comment_by_id(self, user_id: UserId, promo_id: PromoId, comment_id: CommentId) -> None:
        query = (
            select(CommentModel)
            .where(and_(CommentModel.id == comment_id, CommentModel.promo_id == promo_id))
            .options(selectinload(CommentModel.author), selectinload(CommentModel.promo))
        )

        result = await self.db_session.execute(query)
        comment = result.scalars().one_or_none()

        if not comment or not comment.promo:
            raise EntityNotFoundError("Такого промокода или комментария не существует.")

        if str(comment.author_id) != str(user_id):
            raise EntityAccessDeniedError("Комментарий не принадлежит пользователю.")

        await self.db_session.delete(comment)
        await self.db_session.commit()

    async def activate_promo_by_id(self, user_id: UserId, promo_id: PromoId) -> str:
        query = select(PromoModel).where(PromoModel.id == promo_id).options(selectinload(PromoModel.unique_values))

        user_data = await self.get_user_by_id(user_id)

        if not user_data:
            raise EntityUnauthorizedError

        user_age, user_country = user_data.age, user_data.country

        user_target_subquery = self.get_user_promo_target_query(user_age, user_country)
        query = query.where(or_(~PromoModel.targets.any(), PromoModel.id.in_(user_target_subquery)))

        result = await self.db_session.execute(query)
        promo = result.scalars().one_or_none()

        if not promo:
            raise EntityNotFoundError("Промокод не найден.")

        if not promo.is_active:
            raise EntityAccessDeniedError("Вы не можете использовать этот промокод.")

        if promo.mode == PromoModeEnum.COMMON:
            if promo.used_count >= promo.max_count:
                raise EntityAccessDeniedError("Вы не можете использовать этот промокод.")

            promo.used_count += 1
            code = promo.promo_common
        else:
            unique = None
            for value in promo.unique_values:
                if not value.is_used:
                    unique = value
                    break

            if not unique:
                raise EntityAccessDeniedError("Вы не можете использовать этот промокод.")

            code = unique.unique_code
            unique.is_used = True

        activation = UserPromoActivationModel(user_id=user_id, promo_id=promo_id)

        self.db_session.add(activation)

        await self.db_session.commit()
        await self.db_session.refresh(promo)

        return code

    async def get_user_promo_activations_history(
        self, user_id: UserId, limit: int, offset: int
    ) -> tuple[int, Iterable[PromoModel]]:
        query = (
            select(PromoModel)
            .join(
                UserPromoActivationModel,
                UserPromoActivationModel.promo_id == PromoModel.id,
            )
            .where(UserPromoActivationModel.user_id == user_id)
            .options(
                selectinload(PromoModel.liked_by_users),
                selectinload(PromoModel.company),
                selectinload(PromoModel.comments),
                selectinload(PromoModel.activations),
                selectinload(PromoModel.unique_values),
            )
        )

        total_count_query = query.with_only_columns(func.count()).order_by(None)
        total_count = (await self.db_session.execute(total_count_query)).scalar()

        query = query.order_by(UserPromoActivationModel.activated_at.desc()).limit(limit).offset(offset)

        result = await self.db_session.execute(query)
        promos = result.scalars().all()

        return total_count, promos

    @classmethod
    def get_user_promo_active_condition(cls) -> and_:
        now_date = date.today()
        subquery = (
            select(func.count(PromoUniqueValueModel.promo_id))
            .filter(
                PromoUniqueValueModel.promo_id == PromoModel.id,
                PromoUniqueValueModel.is_used.is_(False),
            )
            .scalar_subquery()
        )

        active_cond = and_(
            or_(
                and_(
                    PromoModel.mode == PromoModeEnum.COMMON,
                    PromoModel.used_count < PromoModel.max_count,
                ),
                and_(PromoModel.mode == PromoModeEnum.UNIQUE, subquery > 0),
            ),
            or_(PromoModel.active_from.is_(None), PromoModel.active_from <= now_date),
            or_(PromoModel.active_until.is_(None), PromoModel.active_until >= now_date),
        )

        return active_cond

    @classmethod
    def get_user_promo_target_query(cls, user_age: int, user_country: str) -> select:
        user_target_query = select(PromoTargetModel.promo_id).where(
            and_(
                or_(
                    PromoTargetModel.age_from.is_(None),
                    PromoTargetModel.age_from <= user_age,
                ),
                or_(
                    PromoTargetModel.age_until.is_(None),
                    PromoTargetModel.age_until >= user_age,
                ),
                or_(
                    PromoTargetModel.country.is_(None),
                    func.lower(PromoTargetModel.country) == func.lower(user_country),
                ),
            )
        )

        return user_target_query
