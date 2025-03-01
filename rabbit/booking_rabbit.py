import json
import pika
from logger import logger
from rabbit.config import settings
from rabbit.tasks import send_booking_confirmation_email

def callback(ch, method, properties, body):
    message = json.loads(body)
    booking_details = message['booking']
    user_email = message['email']
    send_booking_confirmation_email(user_email, booking_details)
    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=settings.BOOKING_QUEUE_NAME)
channel.basic_consume(queue=settings.BOOKING_QUEUE_NAME, on_message_callback=callback)
logger.info("Брокер ожидает сообщений (о бронях)")
channel.start_consuming()
