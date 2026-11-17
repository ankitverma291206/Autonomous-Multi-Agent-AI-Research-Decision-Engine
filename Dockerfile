FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir --upgrade "pip>=26.3" \
    && pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "research_engine.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test

USER root
RUN pip install --no-cache-dir ".[dev]"
COPY tests ./tests
RUN chown -R appuser:appuser /app
USER appuser

CMD ["python", "-m", "pytest", "-q"]
