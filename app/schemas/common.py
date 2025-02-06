import re
from datetime import date
from typing import Annotated, Union, List

from pydantic import Field, constr, conint, UUID4, EmailStr, HttpUrl

from app.schemas.enums import PromoModeEnum


Email = Annotated[
    EmailStr,
    Field(
        min_length=8,
        max_length=120,
        description="Email пользователя",
        examples=["cu_fan@edu.hse.ru"],
    ),
]

Password = Annotated[
    constr(
        min_length=8,
        max_length=60,
        pattern=re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"),
    ),
    Field(
        min_length=8,
        max_length=60,
        description="Пароль пользователя/компании. Должен содержать латинские буквы, хотя бы одну заглавную, одну строчную, одну цифру и специальные символы.",
        examples=["HardPa$$w0rd!iamthewinner"],
    ),
]

UserId = Annotated[
    UUID4,
    Field(
        description="Уникальный идентификатор пользователя.",
        examples=["b5d53d5d-e866-44ee-8546-cf01d2e73152"],
    ),
]

UserFirstName = Annotated[
    constr(min_length=1, max_length=100),
    Field(
        min_length=1,
        max_length=100,
        description="Имя пользователя",
        examples=["Мария"],
    ),
]

UserSurname = Annotated[
    constr(min_length=1, max_length=120),
    Field(
        min_length=1,
        max_length=120,
        description="Фамилия пользователя",
        examples=["Федотова"],
    ),
]

UserAvatarURL = Annotated[
    HttpUrl,
    Field(
        max_length=350,
        description="URL аватара пользователя",
        examples=["https://cdn2.thecatapi.com/images/3lo.jpg"],
    ),
]

CompanyId = Annotated[
    UUID4,
    Field(
        description="Уникальный идентификатор компании.",
        examples=["da3ad08d-9b86-41ff-ad70-a30a64d3d170"],
    ),
]

CompanyNameCreate = Annotated[
    constr(min_length=5, max_length=50),
    Field(
        min_length=5,
        max_length=50,
        description="Имя компании.",
        examples=["Шахов production"],
    ),
]

CompanyName = Annotated[
    constr(min_length=5, max_length=50),
    Field(
        min_length=5,
        max_length=50,
        read_only=True,
        description="Имя компании.",
        examples=["Шахов production"],
    ),
]

PromoMaxCount = Union[
    Annotated[
        conint(ge=0, le=100000000, strict=True),
        Field(
            ge=0,
            le=100000000,
            strict=True,
            description="Максимально количество использований, если mode = COMMON. "
            "Его можно редактировать, но если текущее количество активироваций превышает переданное значение, вернется ошибка. "
            "Если число активаций становится равным max_count, сервер переводит промокод в неактивное состояние (active = false). "
            "Если увеличить max_count для неактивного прокомода, он перейдёт в статус активного.",
            examples=[50],
        ),
    ],
    Annotated[
        conint(ge=1, le=1, strict=True),
        Field(
            ge=1,
            le=1,
            strict=True,
            description="При mode = UNIQUE данное поле должно всегда принимать значение 1.",
            examples=[1],
        ),
    ],
]

PromoActiveFrom = Annotated[
    date,
    Field(
        description="Дата начала действия промокода (включительно). Влияет на параметр active.",
        examples=["2022-12-01"],
    ),
]

PromoActiveUntil = Annotated[
    date,
    Field(
        description="Дата окончания действия промокода (включительно). Влияет на параметр active.",
        examples=["2022-12-31"],
    ),
]

PromoCommon = Annotated[
    constr(min_length=5, max_length=30),
    Field(
        min_length=5,
        max_length=30,
        description="Промокод для использования. Обязательный параметр, если mode = COMMON (иначе должен отсутствовать).",
        examples=["sale-10"],
    ),
]

PromoUnique = Annotated[
    List[constr(min_length=3, max_length=30)],
    Field(
        min_length=1,
        max_length=5000,
        description="Список промокодов. Обязательный параметр, если mode = UNIQUE (иначе должен отсутствовать). "
        "Каждое значение может быть выдано пользователю только один раз.",
        examples=[
            "winter-sale-30-abc28f99qa",
            "winter-sale-30-299faab2c",
            "sale-100-winner",
        ],
    ),
]

PromoMode = Annotated[
    PromoModeEnum,
    Field(
        description="Режим промокода. COMMON - один общий промокод, UNIQUE - список промокодов.",
        examples=["COMMON"],
    ),
]

PromoLikeCount = Annotated[
    conint(ge=0, strict=True),
    Field(
        strict=True,
        read_only=True,
        description="Количество лайков у промокода.",
        examples=[20],
    ),
]

PromoUsedCount = Annotated[
    conint(ge=0, strict=True),
    Field(
        strict=True,
        read_only=True,
        description="Сколько раз пользователи активировали данный промокод.",
        examples=[7],
    ),
]

PromoId = Annotated[
    UUID4,
    Field(
        description="Уникальный ID промокода, выдаётся сервером",
        examples=["d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec"],
    ),
]

PromoDescription = Annotated[
    constr(min_length=10, max_length=300, strict=True),
    Field(
        strict=True,
        min_length=10,
        max_length=300,
        description="Описание промокода",
        examples=["Повышенный кэшбек 10% для новых клиентов банка!"],
    ),
]

PromoImageURL = Annotated[
    HttpUrl,
    Field(
        max_length=350,
        description="Ссылка на фото промокода",
        examples=["https://cdn2.thecatapi.com/images/3lo.jpg"],
    ),
]

PromoIsActive = Annotated[
    bool,
    Field(
        default=True,
        read_only=True,
        description="""Активен ли текущий промокод. Этот параметр определяет сервер. Промокод считается активным (и возможным для активации пользователями), если:
            1. Текущая дата входит в указанный промежуток [active_from; active_until] (при наличии).
            2. Для mode = COMMON число активаций меньше max_count.
            3. Для mode = UNIQUE остались неактивированные значения.""",
        examples=[True],
    ),
]

CommentText = Annotated[
    constr(min_length=10, max_length=1000),
    Field(
        min_length=10,
        max_length=1000,
        description="Текст комментария",
        examples=["Отличное предложение, все работает"],
    ),
]

CommentId = Annotated[
    UUID4,
    Field(
        description="Уникальный ID промокода, выдаётся сервером",
        examples=["d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec"],
    ),
]

Country = Annotated[
    constr(min_length=2, max_length=2),
    Field(
        min_length=2,
        max_length=2,
        description="Страна пользователя в формате ISO 3166-1 alpha-2, регистр может быть разным. Страна с данным кодом должна обязательно существовать.",
        examples=["ru"],
    ),
]
