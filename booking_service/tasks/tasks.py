import smtplib
from pydantic import EmailStr

from booking_service.config import settings
from booking_service.tasks.celery import celery
from booking_service.tasks.email_templates import create_booking_confirmation_template, create_pay_confirmation_template

@celery.task
def send_booking_confirmation_email(
    booking: dict,
    email_to: EmailStr,
):
    msg_content = create_booking_confirmation_template(booking, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
    # logger.info(f"Письмо было успешно отправлено по адресу {email_to}")


@celery.task
def send_pay_confirmation_email(
    booking: dict,
    email_to: EmailStr,
):
    msg_content = create_pay_confirmation_template(booking, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
    # logger.info(f"Письмо было успешно отправлено по адресу {email_to}")