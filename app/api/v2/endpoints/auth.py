from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.core.exceptions import InvalidCredentialsError, EmailAlreadyExistsError
from app.schemas.error import ErrorResponse
from app.schemas.user import UserRegister, UserLogin
from app.schemas.business import BusinessCompanyRegister, BusinessCompanyLogin
from app.interactors.caching import CacheAccessTokenInteractor
from app.interactors.auth import (
    SignUpUserInteractor,
    SignInUserInteractor,
    SignUpBusinessCompanyInteractor,
    SignInBusinessCompanyInteractor,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(route_class=DishkaRoute)


@router.post("/user/auth/sign-up")
async def user_sign_up(
    schema: UserRegister,
    interactor: FromDishka[SignUpUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        token = await interactor(user_register=schema, cache_interactor=cache_interactor)
    except EmailAlreadyExistsError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": token})


@router.post("/user/auth/sign-in")
async def user_sign_in(
    schema: UserLogin,
    interactor: FromDishka[SignInUserInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        token = await interactor(user_login=schema, cache_interactor=cache_interactor)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": token})


@router.post("/business/auth/sign-up")
async def business_sign_up(
    schema: BusinessCompanyRegister,
    interactor: FromDishka[SignUpBusinessCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        token, company_id = await interactor(business_company_register=schema, cache_interactor=cache_interactor)
    except EmailAlreadyExistsError as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"token": token, "company_id": company_id},
    )


@router.post("/business/auth/sign-in")
async def business_sign_in(
    schema: BusinessCompanyLogin,
    interactor: FromDishka[SignInBusinessCompanyInteractor],
    cache_interactor: FromDishka[CacheAccessTokenInteractor],
) -> Response:
    try:
        token = await interactor(business_company_login=schema, cache_interactor=cache_interactor)
    except InvalidCredentialsError as exc:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(message=exc.detail).dict(),
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"token": token})
