from celery import Celery

from booking_service.config import settings

celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["booking_service.tasks.tasks"]
)
