import smtplib
from pydantic import EmailStr
from logger import logger
from rabbit.config import settings
from rabbit.email_template import (create_booking_confirmation_template,
                                   create_pay_confirmation_template)


def send_booking_confirmation_email(
    email_to: EmailStr,
    booking: dict,
):
    msg_content = create_booking_confirmation_template(date_from=booking['date_from'],
                                                       date_to=booking['date_to'],
                                                       email_to= email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
        logger.info(f"Письмо о бронировании отправлено на почту пользователю {email_to}")


def send_pay_confirmation_email(
    booking: dict,
    email_to: EmailStr,
):
    msg_content = create_pay_confirmation_template(booking['date_from'],
                                                   booking['date_to'],
                                                   email_to)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
    logger.info(f"Письмо об оплате было успешно отправлено по адресу {email_to}")