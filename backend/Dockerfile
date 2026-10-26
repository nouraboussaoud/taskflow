FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=builder /install /usr/local
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY entrypoint.sh ./entrypoint.sh

RUN useradd --create-home --uid 10001 taskflow && \
    chmod +x /app/entrypoint.sh && \
    chown -R taskflow:taskflow /app
USER taskflow

EXPOSE 8000
CMD ["/app/entrypoint.sh"]
