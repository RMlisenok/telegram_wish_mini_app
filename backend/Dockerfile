FROM python:3.13-slim

WORKDIR /app/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev
COPY . .
ENV PATH="/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "80"]