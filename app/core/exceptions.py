from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas.error import ErrorResponse


class InvalidRequestDataError(Exception):
    def __init__(self, detail="Ошибка в данных запроса."):
        self.detail = detail
        super().__init__(self.detail)


class InvalidCredentialsError(Exception):
    def __init__(self, detail="Неверный email или пароль."):
        self.detail = detail
        super().__init__(self.detail)


class EmailAlreadyExistsError(Exception):
    def __init__(self, detail="Такой email уже зарегистрирован."):
        self.detail = detail
        super().__init__(self.detail)


class EntityUnauthorizedError(Exception):
    def __init__(self, detail="Пользователь не авторизован."):
        self.detail = detail
        super().__init__(self.detail)


class EntityNotFoundError(Exception):
    def __init__(self, detail="Объект не найден"):
        self.detail = detail
        super().__init__(self.detail)


class EntityAccessDeniedError(Exception):
    def __init__(self, detail="Доступ запрещен"):
        self.detail = detail
        super().__init__(self.detail)


async def validation_exception_handler(_: Request, __: ValidationError):
    print(__)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(message="Ошибка в данных запроса.").dict(),
    )


def setup_exception_handlers(app: FastAPI):
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(InvalidRequestDataError, validation_exception_handler)
