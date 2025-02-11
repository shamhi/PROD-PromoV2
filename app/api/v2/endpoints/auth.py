from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.interactors.auth import (
    SignInBusinessCompanyInteractor,
    SignInUserInteractor,
    SignUpBusinessCompanyInteractor,
    SignUpUserInteractor,
)
from app.interactors.caching import CacheAccessTokenInteractor
from app.schemas.business import BusinessCompanyLogin, BusinessCompanyRegister
from app.schemas.error import ErrorResponse
from app.schemas.user import UserLogin, UserRegister

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(route_class=DishkaRoute)


@router.post("/user/auth/sign-up", tags=["B2C"])
async def user_sign_up(
    schema: UserRegister,
    auth_interactor: FromDishka[SignUpUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        token = await auth_interactor(user_register=schema, cache_interactor=cache_interactor)
    except EmailAlreadyExistsError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": token})


@router.post("/user/auth/sign-in", tags=["B2C"])
async def user_sign_in(
    schema: UserLogin,
    auth_interactor: FromDishka[SignInUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        token = await auth_interactor(user_login=schema, cache_interactor=cache_interactor)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": token})


@router.post("/business/auth/sign-up", tags=["B2B"])
async def business_sign_up(
    schema: BusinessCompanyRegister,
    auth_interactor: FromDishka[SignUpBusinessCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        token, company_id = await auth_interactor(business_company_register=schema, cache_interactor=cache_interactor)
    except EmailAlreadyExistsError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"token": token, "company_id": company_id},
    )


@router.post("/business/auth/sign-in", tags=["B2B"])
async def business_sign_in(
    schema: BusinessCompanyLogin,
    auth_interactor: FromDishka[SignInBusinessCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        token = await auth_interactor(business_company_login=schema, cache_interactor=cache_interactor)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": token})
