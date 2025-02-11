from typing import List, Optional

from app.database.repositories.business import BusinessCompanyRepository
from app.schemas.business import PromoCreate, PromoPatch, PromoReadOnly, PromoStat
from app.schemas.common import CompanyId, PromoId
from app.schemas.enums import PromoSortByEnum
from app.utils.serializer import serialize_promo_read_only, serialize_promo_stat


class CreateNewPromoInteractor:
    def __init__(self, business_company_repository: BusinessCompanyRepository):
        self.business_company_repository = business_company_repository

    async def __call__(self, company_id: CompanyId, promo_create: PromoCreate) -> str:
        new_promo = await self.business_company_repository.create_new_promo(company_id, promo_create)

        return str(new_promo.id)


class GetPromosListInteractor:
    def __init__(self, business_company_repository: BusinessCompanyRepository):
        self.business_company_repository = business_company_repository

    async def __call__(
        self,
        company_id: CompanyId,
        sort_by: PromoSortByEnum | None = None,
        country: list[str] | None = None,
        limit: int | None = 10,
        offset: int | None = 0,
    ) -> list[PromoReadOnly]:
        (
            total_count,
            promos,
        ) = await self.business_company_repository.get_promos_for_company(
            company_id=company_id,
            sort_by=sort_by,
            country=country,
            limit=limit,
            offset=offset,
        )

        promos_read_only = [serialize_promo_read_only(promo) for promo in promos]

        return total_count, promos_read_only


class GetPromoByIdInteractor:
    def __init__(self, business_company_repository: BusinessCompanyRepository):
        self.business_company_repository = business_company_repository

    async def __call__(self, company_id: CompanyId, promo_id: PromoId) -> PromoReadOnly:
        promo = await self.business_company_repository.get_company_promo_by_id(company_id=company_id, promo_id=promo_id)

        promo_read_only = serialize_promo_read_only(promo)

        return promo_read_only


class PatchPromoByIdInteractor:
    def __init__(self, business_company_repository: BusinessCompanyRepository):
        self.business_company_repository = business_company_repository

    async def __call__(self, company_id: CompanyId, promo_id: PromoId, promo_patch: PromoPatch) -> PromoReadOnly:
        promo = await self.business_company_repository.patch_company_promo_by_id(
            company_id=company_id, promo_id=promo_id, promo_patch=promo_patch
        )

        promo_read_only = serialize_promo_read_only(promo)

        return promo_read_only


class GetPromoStatByIdInteractor:
    def __init__(self, business_company_repository: BusinessCompanyRepository):
        self.business_company_repository = business_company_repository

    async def __call__(
        self,
        company_id: CompanyId,
        promo_id: PromoId,
    ) -> PromoStat:
        promo = await self.business_company_repository.get_company_promo_by_id(company_id=company_id, promo_id=promo_id)

        promo_activations = await self.business_company_repository.get_promo_activations_by_country(promo_id=promo.id)

        promo_stat = serialize_promo_stat(promo_activations)

        return promo_stat
