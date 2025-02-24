from typing import Annotated
from payment_service.dao import PaymentDAO
from payment_service.exceptions import BookingAlreadyPaid, IncorrectBookingID
import stripe
from datetime import datetime
from pydantic import parse_obj_as
from fastapi import Depends, HTTPException, APIRouter, Header, Request
from payment_service.config import settings
import requests

from payment_service.tasks.tasks import send_pay_confirmation_email

router = APIRouter(prefix="/payments", tags=["Payment microservice"])
api_router = APIRouter(prefix="/api/payments", tags=["for others pais"])

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/pay")
async def pay(request: Request, booking_id: int, stripe_token: Annotated[str | None, Header()] = None):

    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")

    # headers = {'accept': 'application/json', 'token': access_token}
    booking = requests.get(f'http://127.0.0.1:8002/bookings/{booking_id}', headers=headers)
    if booking is None:
        raise IncorrectBookingID
    print(booking.json())
    if booking.json()['payment_status'] == "not paid":
        if stripe_token == None:       # если запрос отправится с api, то в заголовке ничего не будет,
            stripe_token = 'tok_visa'  # поэтому присваиваем токену тестовое значение
        charge = stripe.Charge.create(
            amount=booking.total_cost,
            currency='rub',
            source=stripe_token,
            description='Бронирование отеля',
        )
    else:
        raise BookingAlreadyPaid


    
    # Обновляем статус брони в
    requests.patch(f'http://127.0.0.1:8002/api/bookings/{booking_id}/update-pay', headers=headers)
    # добавляем запись о платеже в БД
    await PaymentDAO.add(user_id=user_response.json()['id'], booking_id=booking.id,
                         amount=booking.total_cost, date_to=datetime.now(), status="success")

    send_pay_confirmation_email.delay(
        date_from=booking.json()['date_from'],
        date_to=booking.json()['date_to'],
        email_to=user_response.json()['email'])
    return {"message": "Оплата проведена успешно", "charge_id": charge.id}




@api_router.delete("/{booking_id}")
async def delete(request: Request, booking_id: int):
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")

    headers = {'accept': 'application/json'}
    booking = requests.get('http://127.0.0.1:8002/bookings/{booking_id}', headers=headers)
    if booking is None:
        raise IncorrectBookingID
    if booking.json()['payment_status'] == "not paid":
        await PaymentDAO.delete(booking_id=booking_id)


