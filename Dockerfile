# ---- Build stage: resolve and install locked dependencies with uv ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Copy only the dependency manifests first so this layer is cached
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# ---- Runtime stage: no uv, no build tooling ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

# Run as a non-root user
RUN useradd --uid 10001 --no-create-home appuser
USER 10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
