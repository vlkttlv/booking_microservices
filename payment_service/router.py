import json
from typing import Annotated
from datetime import datetime
import stripe
import pika
import requests
from fastapi import HTTPException, APIRouter, Header, Request
from logger import logger
from payment_service.dao import PaymentDAO
from payment_service.exceptions import BookingAlreadyPaid, IncorrectBookingID
from payment_service.config import settings

router = APIRouter(prefix="/payments", tags=["Payment microservice"])
api_router = APIRouter(prefix="/api/payments", tags=["for others pais"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/pay")
async def pay(request: Request, booking_id: int, stripe_token: Annotated[str | None, Header()] = None):

    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers, timeout=10)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    
    booking = requests.get(f'http://127.0.0.1:8002/bookings/{booking_id}', headers=headers, timeout=10)
    if booking is None:
        raise IncorrectBookingID
    print(booking.json())
    if booking.json()['payment_status'] == "not paid":
        if stripe_token is None:       # если запрос отправится с api, то в заголовке ничего не будет,
            stripe_token = 'tok_visa'  # поэтому присваиваем токену тестовое значение
        charge = stripe.Charge.create(
            amount=booking.json()['total_cost'],
            currency='rub',
            source=stripe_token,
            description='Бронирование отеля',
        )
    else:
        raise BookingAlreadyPaid
    
    # Обновляем статус брони
    update_booking = requests.patch(f'http://127.0.0.1:8002/api/bookings/{booking_id}/update-pay', headers=headers, timeout=10)
    if update_booking.status_code!= 200:
        raise HTTPException(status_code=update_booking.status_code, detail="Ошибка при изменении статуса брони")
    
    # добавляем запись о платеже в БД
    await PaymentDAO.add(user_id=user_response.json()['id'], booking_id=booking.json()['id'],
                         amount=booking.json()['total_cost'], date_to=datetime.now(), status="success")

    pay_dict = {}
    pay_dict['date_from'] = str(booking.json()['date_from'])
    pay_dict['date_to'] = str(booking.json()['date_to'])
    pay_dict['info'] = 'pay'
    connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
    channel = connection.channel()
    # Подготовка сообщения для RabbitMQ
    message = {
        "booking": pay_dict,
        "email": user_response.json()['email']
    }
    channel.basic_publish(exchange='', routing_key=settings.PAY_QUEUE_NAME, body=json.dumps(message))
    connection.close()
    logger.info("Бронь оплачена")
    return {"message": "Оплата проведена успешно", "charge_id": charge.id}




@api_router.delete("/{booking_id}")
async def delete(request: Request, booking_id: int, token: Annotated[str | None, Header()] = None):
    if token is None:
        token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers, timeout=10)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    await PaymentDAO.delete(booking_id=booking_id)


