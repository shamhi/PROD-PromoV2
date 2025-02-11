from typing import Annotated, Optional

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Path, Query, Response, status
from fastapi.responses import JSONResponse

from app.api.v2.endpoints.auth import oauth2_scheme
from app.core.exceptions import (
    EntityAccessDeniedError,
    EntityNotFoundError,
    EntityUnauthorizedError,
    InvalidRequestDataError,
)
from app.interactors.auth import OAuth2PasswordBearerCompanyInteractor
from app.interactors.business import (
    CreateNewPromoInteractor,
    GetPromoByIdInteractor,
    GetPromosListInteractor,
    GetPromoStatByIdInteractor,
    PatchPromoByIdInteractor,
)
from app.interactors.caching import CacheAccessTokenInteractor
from app.schemas.business import PromoCreate, PromoPatch
from app.schemas.common import PromoId
from app.schemas.enums import PromoSortByEnum
from app.schemas.error import ErrorResponse
from app.utils.serializer import serialize_countries_list

router = APIRouter(route_class=DishkaRoute, prefix="/business", tags=["B2B"])


@router.post("/promo")
async def create_new_promo(
    token: Annotated[str, Depends(oauth2_scheme)],
    schema: PromoCreate,
    business_interactor: FromDishka[CreateNewPromoInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        company_id = await oauth2_interactor(token, cache_interactor)
        promo_id = await business_interactor(company_id=company_id, promo_create=schema)
    except EntityUnauthorizedError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": promo_id})


@router.get("/promo")
async def get_promos_list(
    token: Annotated[str, Depends(oauth2_scheme)],
    business_interactor: FromDishka[GetPromosListInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    sort_by: PromoSortByEnum | None = Query(default=None, description="Сортировать по дате начала/конца действия промокода"),
    country: str | None = Query(
        default=None,
        description="Список стран целевой аудитории в формате ISO 3166-1 alpha-2",
    ),
    limit: int | None = Query(default=10, ge=0, le=100, description="Количество записей на странице"),
    offset: int | None = Query(default=0, ge=0, description="Смещение для пагинации"),
) -> Response:
    try:
        company_id = await oauth2_interactor(token, cache_interactor)
        total_count, promos_list = await business_interactor(
            company_id=company_id,
            sort_by=sort_by,
            country=serialize_countries_list(country),
            limit=limit,
            offset=offset,
        )
    except EntityUnauthorizedError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=promos_list,
        headers={"X-Total-Count": str(total_count)},
    )


@router.get("/promo/{id}")
async def get_promo_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    business_interactor: FromDishka[GetPromoByIdInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        company_id = await oauth2_interactor(token, cache_interactor)
        promo = await business_interactor(company_id=company_id, promo_id=id)
    except EntityUnauthorizedError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except EntityNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except EntityAccessDeniedError as exc:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except InvalidRequestDataError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=promo,
    )


@router.patch("/promo/{id}")
async def patch_promo_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    business_interactor: FromDishka[PatchPromoByIdInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    scheme: PromoPatch,
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        company_id = await oauth2_interactor(token, cache_interactor)
        promo = await business_interactor(company_id=company_id, promo_id=id, promo_patch=scheme)
    except EntityUnauthorizedError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except EntityNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except EntityAccessDeniedError as exc:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except InvalidRequestDataError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=promo,
    )


@router.get("/promo/{id}/stat")
async def get_promo_stat_by_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    business_interactor: FromDishka[GetPromoStatByIdInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        company_id = await oauth2_interactor(token, cache_interactor)
        promo = await business_interactor(company_id=company_id, promo_id=id)
    except EntityUnauthorizedError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except EntityNotFoundError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except EntityAccessDeniedError as exc:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(message=exc.detail).dict(),
        )
    except InvalidRequestDataError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=promo,
    )
