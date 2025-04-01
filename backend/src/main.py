from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from uvicorn import run

from src.config import settings
from src.router import router


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,  # адреса с которых будут идти запросы
        allow_credentials=True,
        allow_methods=["*"],  # TODO: пофиксили? проверить
        allow_headers=["*"],
    )

app.include_router(router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
