FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY markov /app/markov
COPY scripts /app/scripts
COPY config.yaml /app/config.yaml

RUN pip install --no-cache-dir .

EXPOSE 8000 8765

CMD ["python", "-m", "scripts.run_api"]
