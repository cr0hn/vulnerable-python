FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock .
RUN uv sync --locked --no-install-project

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8080

# Seed on start, then run Flask (debug controlled by FLASK_DEBUG)
CMD ["python", "run.py"]
