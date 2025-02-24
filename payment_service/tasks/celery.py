from celery import Celery

from payment_service.config import settings

celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["payment_service.tasks.tasks"]
)
