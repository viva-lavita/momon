FROM python:3.13 as build-image

RUN mkdir /backend
ENV HOME="/backend"

WORKDIR $HOME
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING=utf-8

COPY --from=ghcr.io/astral-sh/uv:0.6.16 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

ADD . ./uv.lock ./pyproject.toml $HOME
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="$HOME/.venv/bin:$PATH"

COPY /scripts /scripts/
RUN chmod a+x /scripts/*
