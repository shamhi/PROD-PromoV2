from typing import List, Optional

from pydantic import Field, conint, constr

from app.schemas.base import CustomBaseModel
from app.schemas.common import (
    CompanyId,
    CompanyName,
    Country,
    Email,
    Password,
    PromoActiveFrom,
    PromoActiveUntil,
    PromoCommon,
    PromoDescription,
    PromoId,
    PromoImageURL,
    PromoIsActive,
    PromoLikeCount,
    PromoMaxCount,
    PromoMode,
    PromoUnique,
    PromoUsedCount,
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

    age_from: conint(ge=0, le=100, strict=True) | None = Field(
        default=None,
        ge=0,
        le=100,
        strict=True,
        description="Минимальный возраст целевой аудитории (включительно). Не должен превышать age_until.",
        examples=[14],
    )
    age_until: conint(ge=0, le=100, strict=True) | None = Field(
        default=None,
        ge=0,
        le=100,
        strict=True,
        description="Максимальный возраст целевой аудитории (включительно).",
        examples=[20],
    )
    country: Country | None = None
    categories: list[constr(min_length=2, max_length=20)] | None = Field(
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
    image_url: PromoImageURL | None = None
    target: Target
    max_count: PromoMaxCount
    active_from: PromoActiveFrom | None = None
    active_until: PromoActiveUntil | None = None
    mode: PromoMode
    promo_common: PromoCommon | None = None
    promo_unique: PromoUnique | None = None


class PromoPatch(CustomBaseModel):
    """
    Поля для редактирования промокода
    """

    description: PromoDescription | None = None
    image_url: PromoImageURL | None = None
    target: Target | None = None
    max_count: PromoMaxCount | None = None
    active_from: PromoActiveFrom | None = None
    active_until: PromoActiveUntil | None = None


class PromoReadOnly(CustomBaseModel):
    """
    Промокод
    """

    description: PromoDescription
    image_url: PromoImageURL | None = None
    target: Target
    max_count: PromoMaxCount
    active_from: PromoActiveFrom | None = None
    active_until: PromoActiveUntil | None = None
    mode: PromoMode
    promo_common: PromoCommon | None = None
    promo_unique: PromoUnique | None = None
    promo_id: PromoId
    company_id: CompanyId
    company_name: CompanyName
    like_count: PromoLikeCount
    used_count: PromoUsedCount
    active: PromoIsActive


class PromoStatCountriesActivations(CustomBaseModel):
    country: Country | None
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
    countries: list[PromoStatCountriesActivations] | None = None
