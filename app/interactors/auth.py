from app.database.repositories.user import UserRepository
from app.database.repositories.business import BusinessCompanyRepository
from app.core.security import verify_password, create_access_token, decode_access_token
from app.core.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    EntityUnauthorizedError,
)
from app.interactors.caching import CacheAccessTokenInteractor
from app.schemas.enums import EntityTypeEnum
from app.schemas.user import UserRegister, UserLogin
from app.schemas.business import BusinessCompanyRegister, BusinessCompanyLogin


class SignUpUserInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_register: UserRegister, cache_interactor: CacheAccessTokenInteractor) -> str:
        exist_user = await self.user_repository.get_user_by_email(user_register.email)
        if exist_user:
            raise EmailAlreadyExistsError

        new_user = await self.user_repository.create_new_user(user_register)

        token = create_access_token({"sub": str(new_user.id), "type": EntityTypeEnum.USER})

        await cache_interactor.save_user_token(new_user.id, token)

        return token


class SignInUserInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def __call__(self, user_login: UserLogin, cache_interactor: CacheAccessTokenInteractor) -> str:
        user = await self.user_repository.get_user_by_email(user_login.email)
        if not user:
            raise InvalidCredentialsError

        if not verify_password(user_login.password, user.password):
            raise InvalidCredentialsError

        token = create_access_token({"sub": str(user.id), "type": EntityTypeEnum.USER})

        await cache_interactor.save_user_token(user.id, token)

        return token


class SignUpBusinessCompanyInteractor:
    def __init__(self, business_company_repository: BusinessCompanyRepository):
        self.business_company_repository = business_company_repository

    async def __call__(
        self,
        business_company_register: BusinessCompanyRegister,
        cache_interactor: CacheAccessTokenInteractor,
    ) -> tuple[str, str]:
        exist_company = await self.business_company_repository.get_company_by_email(business_company_register.email)
        if exist_company:
            raise EmailAlreadyExistsError

        new_company = await self.business_company_repository.create_new_company(business_company_register)

        token = create_access_token({"sub": str(new_company.id), "type": EntityTypeEnum.COMPANY})

        await cache_interactor.save_company_token(new_company.id, token)

        return token, str(new_company.id)


class SignInBusinessCompanyInteractor:
    def __init__(self, business_company_repository: BusinessCompanyRepository):
        self.business_company_repository = business_company_repository

    async def __call__(
        self,
        business_company_login: BusinessCompanyLogin,
        cache_interactor: CacheAccessTokenInteractor,
    ) -> str:
        business_company = await self.business_company_repository.get_company_by_email(business_company_login.email)
        if not business_company:
            raise InvalidCredentialsError

        if not verify_password(business_company_login.password, business_company.password):
            raise InvalidCredentialsError

        token = create_access_token({"sub": str(business_company.id), "type": EntityTypeEnum.COMPANY})

        await cache_interactor.save_company_token(business_company.id, token)

        return token


class OAuth2PasswordBearerUserInteractor:
    async def __call__(self, token: str, cache_interactor: CacheAccessTokenInteractor) -> str:
        decoded_token = decode_access_token(token)
        if not decoded_token:
            raise EntityUnauthorizedError

        entity_type = decoded_token["type"]
        if entity_type != EntityTypeEnum.USER:
            raise EntityUnauthorizedError

        id = decoded_token["sub"]

        cached_token = await cache_interactor.get_user_token(id)
        if cached_token is None or cached_token != token:
            raise EntityUnauthorizedError

        return id


class OAuth2PasswordBearerCompanyInteractor:
    async def __call__(self, token: str, cache_interactor: CacheAccessTokenInteractor) -> str:
        decoded_token = decode_access_token(token)
        if not decoded_token:
            raise EntityUnauthorizedError

        entity_type = decoded_token["type"]
        if entity_type != EntityTypeEnum.COMPANY:
            raise EntityUnauthorizedError

        id = decoded_token["sub"]

        cached_token = await cache_interactor.get_company_token(id)
        if cached_token is None or cached_token != token:
            raise EntityUnauthorizedError

        return id
