from datetime import datetime
from typing import Optional

from pydantic import Field, conint

from app.schemas.base import CustomBaseModel
from app.schemas.common import (
    CommentId,
    CommentText,
    CompanyId,
    CompanyName,
    Country,
    Email,
    Password,
    PromoDescription,
    PromoId,
    PromoImageURL,
    PromoIsActive,
    PromoLikeCount,
    UserAvatarURL,
    UserFirstName,
    UserSurname,
)


class UserTargetSettings(CustomBaseModel):
    """
    Таргет настройки пользователя
    """

    age: conint(ge=0, le=100, strict=True) = Field(
        ge=0,
        le=100,
        strict=True,
        description="Возраст пользователя",
        examples=[13],
    )
    country: Country


class User(CustomBaseModel):
    """
    Пользователь
    """

    name: UserFirstName
    surname: UserSurname
    email: Email
    avatar_url: UserAvatarURL | None = None
    other: UserTargetSettings


class UserRegister(CustomBaseModel):
    """
    Регистрация пользователя
    """

    name: UserFirstName
    surname: UserSurname
    email: Email
    avatar_url: UserAvatarURL | None = None
    other: UserTargetSettings
    password: Password


class UserLogin(CustomBaseModel):
    """
    Вход пользователя
    """

    email: Email
    password: Password


class UserPatch(CustomBaseModel):
    """
    Обновление данных пользователя
    """

    name: UserFirstName | None = None
    surname: UserSurname | None = None
    avatar_url: UserAvatarURL | None = None
    password: Password | None = None


class PromoForUser(CustomBaseModel):
    """
    Поля промокода при получении пользователем
    """

    promo_id: PromoId
    company_id: CompanyId
    company_name: CompanyName
    description: PromoDescription
    image_url: PromoImageURL | None = None
    active: PromoIsActive
    is_activated_by_user: bool = Field(
        description="Активировал ли когда-то пользователь этот промокод",
        examples=[False],
    )
    like_count: PromoLikeCount
    is_liked_by_user: bool = Field(
        description="Поставил ли пользователь лайк этому промокоду",
        examples=[False],
    )
    comment_count: conint(ge=0, strict=True) = Field(
        ge=0,
        strict=True,
        description="Количество комментариев у промокода",
        examples=[5],
    )


class CommentAuthor(CustomBaseModel):
    """
    Автор комментария
    """

    name: UserFirstName
    surname: UserSurname
    avatar_url: UserAvatarURL | None = None


class Comment(CustomBaseModel):
    """
    Комментарий
    """

    id: CommentId
    text: CommentText
    date: datetime = Field(
        description="Дата и время создания комментария. "
        "Часовой пояс может быть любым, необходимо отразить его в формате RFC3339 (с суффиксом Zhh:mm).",
        examples=["2025-01-02T15:04:05Z07:00"],
    )
    author: CommentAuthor


class CommentTextRequest(CustomBaseModel):
    text: CommentText


class AntifraudResponse(CustomBaseModel):
    ok: bool
    cache_until: datetime | None = None
