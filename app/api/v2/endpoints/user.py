from typing import Annotated, Optional

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, Query, Path, Depends, status
from fastapi.responses import JSONResponse

from app.api.v2.endpoints.auth import oauth2_scheme
from app.interactors.auth import OAuth2PasswordBearerUserInteractor
from app.interactors.antifraud import AntifraudInteractor
from app.interactors.caching import CacheAccessTokenInteractor, CacheAntifraudInteractor
from app.interactors.user import (
    GetUserProfileInteractor,
    PatchUserByIdInteractor,
    GetUserPromoFeedInteractor,
    GetUserPromoByIdInteractor,
    AddLikeToPromoInteractor,
    DeleteLikeToPromoInteractor,
    AddCommentToPromoInteractor,
    GetPromoCommentsInteractor,
    GetPromoCommentByIdInteractor,
    EditUserCommentByIdInteractor,
    DeleteUserCommentByIdInteractor,
    UserActivatePromoByIdInteractor,
    GetPromoActivationsHistoryInteractor,
)
from app.core.exceptions import (
    EntityUnauthorizedError,
    EntityAccessDeniedError,
    EntityNotFoundError,
)
from app.schemas.error import ErrorResponse
from app.schemas.common import PromoId, CommentId
from app.schemas.user import UserPatch, CommentTextRequest

router = APIRouter(route_class=DishkaRoute)


@router.get("/profile")
async def get_user_profile(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[GetUserProfileInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        user = await user_interactor(user_id)
    except EntityUnauthorizedError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=user)


@router.patch("/profile")
async def patch_user_profile(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[PatchUserByIdInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    user_patch: UserPatch,
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        user = await user_interactor(user_id, user_patch)
    except EntityUnauthorizedError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=user)


@router.get("/feed")
async def get_user_feed(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[GetUserPromoFeedInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    limit: Optional[int] = Query(default=10, ge=0, le=100, description="Количество записей на странице"),
    offset: Optional[int] = Query(default=0, ge=0, description="Смещение для пагинации"),
    category: Optional[str] = Query(default=None, description="Будут возвращены промокоды с указанной категорией."),
    active: Optional[bool] = Query(
        default=None,
        description="Если поле указано, будут возвращены промокоды с соответствующим значением поля active."
        "Если параметр отсутствует, фильтрация по статусу активности не применяется.",
    ),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        total_count, promos_list = await user_interactor(
            user_id=user_id,
            category=category,
            active=active,
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


@router.post("/promo/{id}/like")
async def user_add_like_to_promo(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[AddLikeToPromoInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        await user_interactor(user_id=user_id, promo_id=id)
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

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


@router.delete("/promo/{id}/like")
async def user_delete_like_to_promo(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[DeleteLikeToPromoInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        await user_interactor(user_id=user_id, promo_id=id)
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

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


@router.post("/promo/{id}/comments")
async def add_comment_to_promo(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[AddCommentToPromoInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    comment_body: CommentTextRequest,
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        comment = await user_interactor(user_id=user_id, promo_id=id, comment_text=comment_body.text)
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

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=comment)


@router.get("/promo/{id}/comments")
async def get_promo_comments(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[GetPromoCommentsInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    limit: Optional[int] = Query(default=10, ge=0, le=100, description="Количество записей на странице"),
    offset: Optional[int] = Query(default=0, ge=0, description="Смещение для пагинации"),
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        _ = await oauth2_interactor(token, cache_interactor)
        total_count, comments = await user_interactor(promo_id=id, limit=limit, offset=offset)
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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=comments,
        headers={"X-Total-Count": str(total_count)},
    )


@router.get("/promo/{id}/comments/{comment_id}")
async def get_promo_comment(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[GetPromoCommentByIdInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
    comment_id: CommentId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        _ = await oauth2_interactor(token, cache_interactor)
        comment = await user_interactor(promo_id=id, comment_id=comment_id)
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

    return JSONResponse(status_code=status.HTTP_200_OK, content=comment)


@router.put("/promo/{id}/comments/{comment_id}")
async def edit_user_comment(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[EditUserCommentByIdInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    comment_body: CommentTextRequest,
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
    comment_id: CommentId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        comment = await user_interactor(
            user_id=user_id,
            promo_id=id,
            comment_id=comment_id,
            comment_text=comment_body.text,
        )
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

    return JSONResponse(status_code=status.HTTP_200_OK, content=comment)


@router.delete("/promo/{id}/comments/{comment_id}")
async def delete_user_comment(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[DeleteUserCommentByIdInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
    comment_id: CommentId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        await user_interactor(user_id=user_id, promo_id=id, comment_id=comment_id)
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

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


@router.post("/promo/{id}/activate")
async def activate_promo(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[UserActivatePromoByIdInteractor],
    antifraud_interactor: FromDishka[AntifraudInteractor],
    caching_interactor: FromDishka[CacheAntifraudInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        promo_code = await user_interactor(
            user_id=user_id,
            promo_id=str(id),
            antifraud_interactor=antifraud_interactor,
            caching_interactor=caching_interactor,
        )
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

    return JSONResponse(status_code=status.HTTP_200_OK, content={"promo": promo_code})


@router.get("/promo/history")
async def get_user_activations_history(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_interactor: FromDishka[GetPromoActivationsHistoryInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    limit: Optional[int] = Query(default=10, ge=0, le=100, description="Количество записей на странице"),
    offset: Optional[int] = Query(default=0, ge=0, description="Смещение для пагинации"),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        total_count, promos_list = await user_interactor(user_id=user_id, limit=limit, offset=offset)
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
    user_interactor: FromDishka[GetUserPromoByIdInteractor],
    oauth2_interactor: FromDishka[OAuth2PasswordBearerUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
    id: PromoId = Path(
        description="Уникальный ID промокода, выдаётся сервером",
        example="d8f9a687-4ff9-4976-a05c-f1bf1e5e2eec",
    ),
) -> Response:
    try:
        user_id = await oauth2_interactor(token, cache_interactor)
        promo = await user_interactor(user_id=user_id, promo_id=id)
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

    return JSONResponse(status_code=status.HTTP_200_OK, content=promo)
