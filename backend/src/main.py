from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from src.config import app_configs, settings
from src.initial_data import init
from src.router import router


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    # добавить редис, селери и пр.
    if settings.ENVIRONMENT.is_local:
        await init()
    yield


app = FastAPI(
    **app_configs,
    title=settings.PROJECT_NAME,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,  # адреса с которых будут идти запросы
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
        allow_headers=[
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Authorization",
        ],
    )

app.include_router(router)


if __name__ == "__main__":  # для отладки локально вне контейнеров
    if settings.ENVIRONMENT.is_debug:
        import uvicorn

        uvicorn.run(
            app="main:app",
            host="localhost",
            port=8000,
            reload=True,
        )
