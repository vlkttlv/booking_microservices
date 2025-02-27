from datetime import date, datetime
import json
from typing import Annotated
import pika
import requests
from fastapi import APIRouter, Depends, HTTPException, Header, Query, Request
from pydantic import parse_obj_as
from booking_service.exceptions import RoomCannotBeBooked
from booking_service.dao import BookingDAO

from booking_service.utils import check_current_user
from booking_service.config import settings
router = APIRouter(prefix="/bookings", tags=["Бронирования"])
api_router = APIRouter(prefix="/api/bookings", tags=["for others apis"])

@api_router.get("/all", summary="Returns all bookings for the specified period")
async def get_booked_rooms(
    date_from: date = Query(default=datetime.now().date(),
                            description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(default=datetime.now().date(),
                          description=f"Например, {datetime.now().date()}")):
    """Возвращает все брони заданного периода"""
    return await BookingDAO.get_booked_rooms(date_from, date_to)


@router.get("/", summary="Returns all the user's bookings")
async def get_bookings(current_user = Depends(check_current_user)):
    """Получение всех бронирований пользователя"""
    rooms = requests.get('http://127.0.0.1:8001/api/hotels/rooms',
                         headers={'accept':'application/json'}, timeout=10)
    return await BookingDAO.find_all(rooms.json(), user_id=current_user['id'])

@router.get("/{booking_id}", summary="Returns the user's booking by ID")
async def get_booking(booking_id: int, request: Request,
                      token: Annotated[str | None, Header()] = None):
    """Получение бронирования пользователя по ID"""
    if token is None:
        token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers, timeout=10)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    return await BookingDAO.find_one_or_none(id=booking_id, user_id=user_response.json()['id'])

@router.post("/")
async def add_booking(request: Request,
                      room_id: int,
                      date_from: date = Query(default=datetime.now().date(),
                            description=f"Например, {datetime.now().date()}"),
                      date_to: date = Query(default=datetime.now().date(),
                            description=f"Например, {datetime.now().date()}")):
    """Добавление бронирование"""
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers, timeout=10)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    rooms = requests.get('http://127.0.0.1:8001/api/hotels/rooms',
                         headers={'accept':'application/json'}, timeout=10)
    booking = await BookingDAO.add(rooms.json(), user_response.json()['id'],
                                   room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked
    booking_dict = {}
    booking_dict['date_from'] = str(booking.date_from)
    booking_dict['date_to'] = str(booking.date_to)
    # send_booking_confirmation_email.delay(booking_dict, user_response.json()['email'])
    connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
    channel = connection.channel()
        # Подготовка сообщения для RabbitMQ
    message = {
        "booking": booking_dict,
        "email": user_response.json()['email']
    }
    channel.basic_publish(exchange='', routing_key=settings.QUEUE_NAME, body=json.dumps(message))
    connection.close()
    print("Уведомление отправлено в брокер")



@router.delete("/{booking_id}",  status_code=204)
async def delete_booking(booking_id: int, request: Request):
    """Удаление брони"""
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers, timeout=10)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    requests.delete(f'http://127.0.0.1:8003/api/payments/{booking_id}', headers=headers, timeout=10)
    await BookingDAO.delete(user_id=user_response.json()['id'], id=booking_id)


@api_router.patch("/{booking_id}/update-pay")
async def update_payment_status(booking_id: int, request: Request,
                                token: Annotated[str | None, Header()] = None):
    """Изменение статуса на <pay>"""
    if token is None:
        token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': token}
    print(token)
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers, timeout=10)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    await BookingDAO.update(id=booking_id, payment_status='pay')
