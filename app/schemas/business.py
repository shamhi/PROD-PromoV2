from typing import Optional, List

from pydantic import Field, constr, conint

from app.schemas.base import CustomBaseModel
from app.schemas.common import (
    Email,
    Password,
    PromoDescription,
    PromoImageURL,
    PromoMaxCount,
    PromoActiveFrom,
    PromoActiveUntil,
    PromoMode,
    PromoCommon,
    PromoUnique,
    PromoId,
    CompanyId,
    CompanyName,
    PromoLikeCount,
    PromoUsedCount,
    PromoIsActive,
    Country,
)


class BusinessCompanyRegister(CustomBaseModel):
    """
    Регистрация новой компании
    """

    name: CompanyName
    email: Email
    password: Password


class BusinessCompanyLogin(CustomBaseModel):
    """
    Аутентификация компании
    """

    email: Email
    password: Password


class Target(CustomBaseModel):
    """
    Целевая аудитория
    """

    age_from: Optional[conint(ge=0, le=100, strict=True)] = Field(
        default=None,
        ge=0,
        le=100,
        strict=True,
        description="Минимальный возраст целевой аудитории (включительно). Не должен превышать age_until.",
        examples=[14],
    )
    age_until: Optional[conint(ge=0, le=100, strict=True)] = Field(
        default=None,
        ge=0,
        le=100,
        strict=True,
        description="Максимальный возраст целевой аудитории (включительно).",
        examples=[20],
    )
    country: Optional[Country] = None
    categories: Optional[List[constr(min_length=2, max_length=20)]] = Field(
        default=None,
        max_length=20,
        description="Категории для таргетинга.",
        examples=["ios", "коты", "футбол", "учитель"],
    )


class PromoCreate(CustomBaseModel):
    """
    Поля для создания промокода
    """

    description: PromoDescription
    image_url: Optional[PromoImageURL] = None
    target: Target
    max_count: PromoMaxCount
    active_from: Optional[PromoActiveFrom] = None
    active_until: Optional[PromoActiveUntil] = None
    mode: PromoMode
    promo_common: Optional[PromoCommon] = None
    promo_unique: Optional[PromoUnique] = None


class PromoPatch(CustomBaseModel):
    """
    Поля для редактирования промокода
    """

    description: Optional[PromoDescription] = None
    image_url: Optional[PromoImageURL] = None
    target: Optional[Target] = None
    max_count: Optional[PromoMaxCount] = None
    active_from: Optional[PromoActiveFrom] = None
    active_until: Optional[PromoActiveUntil] = None


class PromoReadOnly(CustomBaseModel):
    """
    Промокод
    """

    description: PromoDescription
    image_url: Optional[PromoImageURL] = None
    target: Target
    max_count: PromoMaxCount
    active_from: Optional[PromoActiveFrom] = None
    active_until: Optional[PromoActiveUntil] = None
    mode: PromoMode
    promo_common: Optional[PromoCommon] = None
    promo_unique: Optional[PromoUnique] = None
    promo_id: PromoId
    company_id: CompanyId
    company_name: CompanyName
    like_count: PromoLikeCount
    used_count: PromoUsedCount
    active: PromoIsActive


class PromoStatCountriesActivations(CustomBaseModel):
    country: Optional[Country]
    activations_count: conint(ge=1, strict=True) = Field(
        ge=1,
        strict=True,
        description="Количество активаций в этой стране.",
        examples=[150],
    )


class PromoStat(CustomBaseModel):
    """
    Статистика промокода
    """

    activations_count: conint(ge=0, strict=True) = Field(
        ge=0,
        strict=True,
        description="Общее количество активаций",
        examples=[50],
    )
    countries: Optional[List[PromoStatCountriesActivations]] = None
