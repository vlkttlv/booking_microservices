import json
import pika
from logger import logger
from rabbit.config import settings
from rabbit.tasks import send_pay_confirmation_email

def callback(ch, method, properties, body):
    message = json.loads(body)
    booking_details = message['booking']
    user_email = message['email']
    send_pay_confirmation_email(booking_details, user_email)
    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=settings.PAY_QUEUE_NAME)
channel.basic_consume(queue=settings.PAY_QUEUE_NAME, on_message_callback=callback)
logger.info("Брокер ожидает сообщений (об оплате)")
channel.start_consuming()
