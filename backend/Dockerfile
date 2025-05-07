# Шаг #1 | Building an image
FROM python:3.13 as build-image

# Шаг #2 | Файлы, переменные и группы
# PYTHONUNBUFFERED - Буферизация логов в контейнере stdout и stderr - 0 отключить
# Добавление в группу docker, чтобы иметь возможность использовать команды docker без root в будущем
ENV APP_ROOT /src
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:${APP_ROOT}"
ENV APP_USER service_user

RUN groupadd -r docker \
    && useradd -r -m \
    --home-dir ${APP_ROOT} \
    -s /usr/sbin/nologin \
    -g docker ${APP_USER}
RUN usermod -aG sudo ${APP_USER}

# Шаг #3 Installing uv
FROM build-image as uv-init

ARG APP_ROOT

WORKDIR ${APP_ROOT}

COPY --from=ghcr.io/astral-sh/uv:0.6.16 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Шаг #4 | Installing dependencies
FROM uv-init as uv-install

ADD . ./uv.lock ./pyproject.toml $APP_ROOT

# монтрование кэша иобновление зависимостей без переустановки всего проекта
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# venv activate
ENV PATH="$APP_ROOT/.venv/bin:$PATH"

# Шаг #5 | Run-app
FROM uv-install as run-app

RUN chmod a+x scripts/*

# . -> APP_ROOT /src
COPY . .

# TODO: потом переноси эту команду в компоуз
CMD ["./scripts/start-dev.sh"]
