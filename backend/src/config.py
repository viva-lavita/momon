# TODO; с усложнением разбить настройки по назначениям (бд, тест, эмейл и тд)
# TODO; добавить отключение документации api на проде

import secrets
from typing import Annotated, Any

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    computed_field,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.constants import Environment


def parse_cors(v: Any) -> list[str] | str:
    """Parse a string or list of strings into a list of strings."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class PostgresDBSettings(BaseSettings):
    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_ECHO: bool

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return str(
            MultiHostUrl.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )


class Settings(BaseSettings):
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]


settings = [
    PostgresDBSettings,
    Settings,
]


class AppSettings(*settings):
    APP_VERSION: str = "1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Environment = Environment.LOCAL
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = AppSettings()

app_configs = {}

if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/api/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["debug"] = False
    app_configs["openapi_url"] = None
    app_configs["docs_url"] = None
    app_configs["redoc_url"] = None

if settings.ENVIRONMENT.is_debug:
    app_configs["debug"] = True
    app_configs["openapi_url"] = "/openapi.json"
    app_configs["docs_url"] = "/docs"
    app_configs["redoc_url"] = "/redoc"
