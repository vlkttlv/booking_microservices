FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . /app/users_service
COPY logger.py /app/logger.py

WORKDIR /app
ENV PYTHONPATH=/app
CMD ["sh", "-c", "cd users_service && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]



