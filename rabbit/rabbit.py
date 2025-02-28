import json
from logger import logger
import pika
from rabbit.config import settings
from rabbit.tasks import send_booking_confirmation_email, send_pay_confirmation_email

def callback(ch, method, properties, body):
    message = json.loads(body)
    booking_details = message['booking']
    user_email = message['email']
    if 'info' in message:
        send_pay_confirmation_email(user_email, booking_details)
    send_booking_confirmation_email(user_email, booking_details)
    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
channel = connection.channel()

channel.queue_declare(queue=settings.QUEUE_NAME)

channel.basic_consume(queue=settings.QUEUE_NAME, on_message_callback=callback)
logger.info("брокер ожидает сообщений")

channel.start_consuming()