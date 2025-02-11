import contextlib

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v2 import root_router
from app.core.build import create_async_container
from app.core.config import create_config
from app.core.exceptions import setup_exception_handlers
from app.ioc.registry import get_providers


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    return app


def configure_app(app: FastAPI, root_router: APIRouter) -> None:
    app.include_router(root_router, prefix="/api")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_exception_handlers(app)

    container = create_async_container(get_providers())
    setup_dishka(container, app)


def main():
    app = create_app()
    configure_app(app, root_router)

    config = create_config()

    host = config.server_config.SERVER_ADDRESS
    port = config.server_config.SERVER_PORT

    if ":" in host:
        host, port = host.split(":")

    uvicorn.run(app, host=host, port=int(port))


if __name__ == "__main__":
    main()
