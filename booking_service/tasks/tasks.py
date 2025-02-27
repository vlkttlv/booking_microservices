# import json
# import smtplib
# import pika
# from pydantic import EmailStr
# from pika import ConnectionParameters
# from booking_service.config import settings
# from booking_service.tasks.celery import celery
# from booking_service.tasks.email_templates import create_booking_confirmation_template

# def send_booking_confirmation_email(
#     email_to: EmailStr,
#     booking: dict,
# ):
#     msg_content = create_booking_confirmation_template(date_from=booking.date_from, date_to=booking.date_to,
#                                                        email_to= email_to)

#     with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#         server.login(settings.SMTP_USER, settings.SMTP_PASS)
#         server.send_message(msg_content)

# def callback(ch, method, properties, body):
#     message = json.loads(body)
#     booking_details = message['booking']
#     print(booking_details)
#     user_email = message['email']
#     send_booking_confirmation_email(user_email, booking_details)
#     ch.basic_ack(delivery_tag=method.delivery_tag)


# connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
# channel = connection.channel()

# channel.queue_declare(queue=settings.QUEUE_NAME)

# channel.basic_consume(queue=settings.QUEUE_NAME, on_message_callback=callback)
# print("Ожидаю сообщений")

# channel.start_consuming()