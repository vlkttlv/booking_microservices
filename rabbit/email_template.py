from email.message import EmailMessage
from pydantic import EmailStr
from rabbit.config import settings


def create_booking_confirmation_template(
    date_from: str,
    date_to: str,
    email_to: EmailStr,
):
    email = EmailMessage()

    email["Subject"] = "Подтверждение бронирования"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <h1>Подтвердите бронирование и оплатите его</h1>
            Вы забронировали отель с {date_from} по {date_to}
        """,
        subtype="html"
    )
    return email


def create_pay_confirmation_template(
        
    date_from,
    date_to,
    email_to: EmailStr,
):
    email = EmailMessage()

    email["Subject"] = "Оплата прошла успешно"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <h1>Поздравляем, оплата прошла успешно!</h1>
            Приятного отдыха!
            Вы оплатили комнату в отеле с {date_from} по {date_to}

        """,
        subtype="html"
    )
    return email