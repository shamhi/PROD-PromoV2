import json
from typing import List, Optional, Tuple

from app.database.postgres.models import CommentModel, PromoModel, UserModel
from app.schemas.business import (
    PromoReadOnly,
    PromoStat,
    PromoStatCountriesActivations,
    Target,
)
from app.schemas.common import Country, UserId
from app.schemas.enums import PromoModeEnum
from app.schemas.user import (
    AntifraudResponse,
    Comment,
    CommentAuthor,
    PromoForUser,
    User,
    UserTargetSettings,
)
from app.utils.time import format_rfc3339_date


def serialize_promo_read_only(promo: PromoModel) -> PromoReadOnly:
    target = Target()
    if promo.targets:
        target_data = promo.targets[0]
        target = Target(
            age_from=target_data.age_from,
            age_until=target_data.age_until,
            country=target_data.country,
            categories=target_data.categories,
        )

    promo_code = (
        promo.promo_common
        if promo.mode == PromoModeEnum.COMMON
        else [unique_value.unique_code for unique_value in promo.unique_values]
    )

    promo_read_only = PromoReadOnly(
        description=promo.description,
        image_url=promo.image_url,
        target=target,
        max_count=promo.max_count,
        active_from=promo.active_from,
        active_until=promo.active_until,
        mode=promo.mode,
        promo_common=promo.promo_common if promo.mode == PromoModeEnum.COMMON else None,
        promo_unique=promo_code if promo.mode == PromoModeEnum.UNIQUE else None,
        promo_id=promo.id,
        company_id=promo.company_id,
        company_name=promo.company.name,
        like_count=len(promo.liked_by_users),
        used_count=promo.used_count,
        active=promo.is_active,
    )

    return json.loads(promo_read_only.json(exclude_none=True))


def serialize_promo_stat(promo_activations: list[tuple[str, int]]) -> PromoStat:
    activations_count = sum(activation_count for _, activation_count in promo_activations)

    countries = [
        PromoStatCountriesActivations(country=country, activations_count=activation_count)
        for country, activation_count in promo_activations
        if activation_count > 0
    ]

    promo_stat = PromoStat(activations_count=activations_count, countries=countries)

    return json.loads(promo_stat.json(exclude_none=True))


def serialize_user(user_orm: UserModel) -> dict:
    user_target_settings = UserTargetSettings(age=user_orm.age, country=user_orm.country)

    user = User(
        name=user_orm.name,
        surname=user_orm.surname,
        email=user_orm.email,
        avatar_url=user_orm.avatar_url,
        other=user_target_settings,
    )

    return json.loads(user.json(exclude_none=True))


def serialize_promo_for_user(promo: PromoModel, user_id: UserId) -> PromoForUser:
    promo_for_user = PromoForUser(
        promo_id=promo.id,
        company_id=promo.company_id,
        company_name=promo.company.name,
        description=promo.description,
        image_url=promo.image_url,
        active=promo.is_active,
        is_activated_by_user=any(str(activation.user_id) == str(user_id) for activation in promo.activations),
        like_count=len(promo.liked_by_users),
        is_liked_by_user=any(user for user in promo.liked_by_users if str(user.id) == str(user_id)),
        comment_count=len(promo.comments),
    )

    return json.loads(promo_for_user.json(exclude_none=True))


def serialize_comment(comment_orm: CommentModel) -> Comment:
    author = CommentAuthor(
        name=comment_orm.author.name,
        surname=comment_orm.author.surname,
        avatar_url=comment_orm.author.avatar_url,
    )

    comment = Comment(
        id=comment_orm.id,
        text=comment_orm.text,
        date=format_rfc3339_date(comment_orm.date, "03:00"),
        author=author,
    )

    return json.loads(comment.json(exclude_none=True))


def serialize_antifraud_response(antifraud_response: AntifraudResponse):
    return json.loads(antifraud_response.json(exclude_none=True))


def serialize_countries_list(country: str) -> list[Country] | None:
    if country:
        countries = [Country(cnt.strip()) for cnt in country.split(",")]
        return countries
