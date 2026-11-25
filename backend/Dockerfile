# syntax=docker/dockerfile:1
# Multi-stage, non-root. See docs/08-operations/DEPLOYMENT.md §3.

# ── build: resolve dependencies into /app/.venv (no dev tools in the final image)
FROM python:3.13-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /usr/local/bin/uv
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# ── final
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod
RUN useradd --system --no-create-home --uid 10001 app
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY config ./config
COPY galeway ./galeway
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request as u; u.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8000\")}/api/v1/health', timeout=4)"
# --forwarded-allow-ips="*" is acceptable only because the host's proxy is the sole route
# to this container (DEPLOYMENT.md §3). Client IPs are read from the configured header.
CMD ["sh", "-c", "exec uvicorn config.asgi:application --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
