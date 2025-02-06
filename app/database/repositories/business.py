from datetime import date
from typing import Optional, Iterable, List, Tuple

from sqlalchemy import or_, desc, func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres.models import (
    BusinessCompanyModel,
    PromoModel,
    PromoTargetModel,
    PromoUniqueValueModel,
    UserPromoActivationModel,
    UserModel,
)
from app.core.security import get_password_hash
from app.core.exceptions import (
    EntityNotFoundError,
    EntityAccessDeniedError,
    InvalidRequestDataError,
)
from app.schemas.enums import PromoModeEnum, PromoSortByEnum
from app.schemas.common import PromoId, CompanyId, Email, Country
from app.schemas.business import BusinessCompanyRegister, PromoCreate, PromoPatch


class BusinessCompanyRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_new_company(self, company: BusinessCompanyRegister) -> BusinessCompanyModel:
        hashed_password = get_password_hash(company.password)
        new_company = BusinessCompanyModel(
            name=company.name,
            email=company.email,
            password=hashed_password,
        )

        self.db_session.add(new_company)
        await self.db_session.commit()
        await self.db_session.refresh(new_company)

        return new_company

    async def get_company_by_email(self, email: Email) -> BusinessCompanyModel:
        query = select(BusinessCompanyModel).where(BusinessCompanyModel.email == email)
        result = await self.db_session.execute(query)

        return result.scalars().one_or_none()

    async def create_new_promo(self, company_id: CompanyId, promo: PromoCreate) -> PromoModel:
        new_promo = PromoModel(
            description=promo.description,
            image_url=str(promo.image_url) if promo.image_url else None,
            max_count=promo.max_count,
            active_from=promo.active_from,
            active_until=promo.active_until,
            mode=promo.mode,
            promo_common=promo.promo_common,
            company_id=company_id,
        )

        self.db_session.add(new_promo)
        await self.db_session.flush()

        new_target_promo = PromoTargetModel(
            promo_id=new_promo.id,
            age_from=promo.target.age_from,
            age_until=promo.target.age_until,
            country=promo.target.country,
            categories=promo.target.categories,
        )

        self.db_session.add(new_target_promo)
        await self.db_session.flush()

        if promo.mode == PromoModeEnum.UNIQUE:
            unique_values = [
                PromoUniqueValueModel(promo_id=new_promo.id, unique_code=value) for value in promo.promo_unique
            ]
            self.db_session.add_all(unique_values)

        await self.db_session.commit()
        await self.db_session.refresh(new_promo)

        return new_promo

    async def get_promos_for_company(
        self,
        company_id: CompanyId,
        sort_by: Optional[PromoSortByEnum] = None,
        country: Optional[List[Country]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[int, Iterable[PromoModel]]:
        query = (
            select(PromoModel)
            .options(
                selectinload(PromoModel.targets),
                selectinload(PromoModel.unique_values),
                selectinload(PromoModel.liked_by_users),
                selectinload(PromoModel.company),
            )
            .where(PromoModel.company_id == company_id)
        )

        if country:
            country_lower = [c.lower() for c in country]
            query = query.outerjoin(PromoTargetModel, PromoTargetModel.promo_id == PromoModel.id).where(
                or_(
                    PromoTargetModel.country.is_(None),
                    func.lower(PromoTargetModel.country).in_(country_lower),
                )
            )

        total_count_query = query.with_only_columns(func.count()).order_by(None)
        total_count = (await self.db_session.execute(total_count_query)).scalar()

        if sort_by == PromoSortByEnum.ACTIVE_FROM:
            query = query.order_by(desc(func.coalesce(PromoModel.active_from, date.min)))
        elif sort_by == PromoSortByEnum.ACTIVE_UNTIL:
            query = query.order_by(desc(func.coalesce(PromoModel.active_until, date.max)))
        else:
            query = query.order_by(desc(PromoModel.created_at))

        query = query.limit(limit).offset(offset)

        result = await self.db_session.execute(query)
        promos = result.scalars().all()

        return total_count, promos

    async def get_company_promo_by_id(self, company_id: CompanyId, promo_id: PromoId) -> PromoModel:
        query = (
            select(PromoModel)
            .options(
                selectinload(PromoModel.targets),
                selectinload(PromoModel.unique_values),
                selectinload(PromoModel.liked_by_users),
                selectinload(PromoModel.company),
                selectinload(PromoModel.activations),
            )
            .where(PromoModel.id == promo_id)
        )

        result = await self.db_session.execute(query)
        promo = result.scalars().one_or_none()

        if not promo:
            raise EntityNotFoundError("Промокод не найден.")

        if str(promo.company_id) != company_id:
            raise EntityAccessDeniedError("Промокод не принадлежит этой компании.")

        return promo

    async def patch_company_promo_by_id(
        self, company_id: CompanyId, promo_id: PromoId, promo_patch: PromoPatch
    ) -> PromoModel:
        query = (
            select(PromoModel)
            .options(
                selectinload(PromoModel.targets),
                selectinload(PromoModel.unique_values),
                selectinload(PromoModel.liked_by_users),
                selectinload(PromoModel.company),
            )
            .where(PromoModel.id == promo_id)
            .with_for_update()
        )

        result = await self.db_session.execute(query)
        promo = result.scalars().one_or_none()

        if not promo:
            raise EntityNotFoundError("Промокод не найден.")

        if str(promo.company_id) != company_id:
            raise EntityAccessDeniedError("Промокод не принадлежит этой компании.")

        if promo.mode == PromoModeEnum.UNIQUE and promo_patch.max_count is not None:
            if promo_patch.max_count != 1:
                raise InvalidRequestDataError

        if promo_patch.description is not None:
            promo.description = promo_patch.description
        if promo_patch.image_url is not None:
            promo.image_url = str(promo_patch.image_url)
        if promo_patch.max_count is not None:
            if promo_patch.max_count < promo.used_count:
                raise InvalidRequestDataError

            promo.max_count = promo_patch.max_count
        if promo_patch.active_from is not None:
            promo.active_from = promo_patch.active_from
        if promo_patch.active_until is not None:
            promo.active_until = promo_patch.active_until

        if promo_patch.target is not None:
            target = promo.targets[0] if promo.targets else PromoTargetModel(promo_id=promo.id)
            target.age_from = promo_patch.target.age_from
            target.age_until = promo_patch.target.age_until
            target.country = promo_patch.target.country
            target.categories = promo_patch.target.categories
            self.db_session.add(target)

        await self.db_session.commit()
        await self.db_session.refresh(promo)

        return promo

    async def get_promo_activations_by_country(self, promo_id: PromoId) -> List[Tuple[str, int]]:
        query = (
            select(
                func.lower(UserModel.country).label("country"),
                func.count(UserPromoActivationModel.id).label("activations_count"),
            )
            .join(UserModel, UserModel.id == UserPromoActivationModel.user_id)
            .where(UserPromoActivationModel.promo_id == promo_id)
            .group_by(func.lower(UserModel.country))
            .order_by(func.lower(UserModel.country).asc())
        )

        result = await self.db_session.execute(query)
        return result.all()
