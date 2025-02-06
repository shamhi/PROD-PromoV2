import contextlib

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dishka.integrations.fastapi import setup_dishka

from app.api.v2 import api_router
from app.core.config import Config
from app.core.ioc_container import container
from app.core.exceptions import setup_exception_handlers


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()


def main():
    app = FastAPI(lifespan=lifespan)
    app.include_router(api_router, prefix="/api")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_exception_handlers(app)
    setup_dishka(container, app)

    host = Config.SERVER_ADDRESS
    port = Config.SERVER_PORT

    if ":" in Config.SERVER_ADDRESS:
        host, port = Config.SERVER_ADDRESS.split(":")

    uvicorn.run(app, host=host, port=int(port))


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        main()
