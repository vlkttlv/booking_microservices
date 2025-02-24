import smtplib
from pydantic import EmailStr

from payment_service.config import settings
from payment_service.tasks.celery import celery
from payment_service.tasks.email_templates import create_pay_confirmation_template


@celery.task
def send_pay_confirmation_email(
    date_from,
    date_to,
    email_to: EmailStr,
):
    msg_content = create_pay_confirmation_template(date_from, date_to, email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
    # logger.info(f"Письмо было успешно отправлено по адресу {email_to}")