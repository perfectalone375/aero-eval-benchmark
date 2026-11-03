FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY deliverables/ ./deliverables/

RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

FROM base AS test
CMD ["pytest", "-v", "tests/"]

FROM base AS runtime
ENTRYPOINT ["aeroeval"]
CMD ["list"]
