from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Query, Request, HTTPException
from pydantic import parse_obj_as
from booking_service.exceptions import IncorrectBookingID, RoomCannotBeBooked
from booking_service.dao import BookingDAO
import requests

from booking_service.schemas import SBooking, UpdateBooking
from booking_service.tasks.tasks import send_booking_confirmation_email

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
async def get_bookings(request: Request):
    """Получение всех бронирований пользователя"""
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    rooms = requests.get('http://127.0.0.1:8001/api/hotels/rooms', headers={'accept':'application/json'})
    return await BookingDAO.find_all(rooms.json(), user_id=user_response.json()['id'])

@router.get("/{booking_id}", summary="Returns the user's booking by ID")
async def get_booking(booking_id: int, request: Request):
    """Получение бронирования пользователя по ID"""
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
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
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    rooms = requests.get('http://127.0.0.1:8001/api/hotels/rooms', headers={'accept':'application/json'})
    booking = await BookingDAO.add(rooms.json(), user_response.json()['id'], room_id, date_from, date_to)
    if not booking:
        raise RoomCannotBeBooked
    booking_dict = parse_obj_as(SBooking, booking).dict()
    send_booking_confirmation_email.delay(booking_dict, user_response.json()['email'])


@router.delete("/{booking_id}",  status_code=204)
async def delete_booking(booking_id: int, request: Request):
    """Удаление брони"""
    # await PaymentDAO.delete(booking_id=booking_id)
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
    if user_response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    await BookingDAO.delete(user_id=user_response.json()['id'], id=booking_id)

# @router.patch("/{booking_id}/pay")
# async def update_payment_status(booking_id: int, update_booking: UpdateBooking, request: Request):
#     booking = await BookingDAO.find_by_id(booking_id=booking_id)
#     access_token = request.cookies.get("booking_access_token")
#     headers = {'accept': 'application/json', 'token': access_token}
#     user_response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
#     if user_response.status_code == 401:
#         raise HTTPException(status_code=401, detail="Not authorized")
#     booking = await BookingDAO.find_by_id(booking_id=booking_id, user_id=user_response.json()['id'])
#     if booking is None:
#         raise IncorrectBookingID
#     if update_booking.date_to is not None and update_booking.date_from is not None:
#         if update_booking.date_from >= update_booking.date_to:
#             raise ValueError
#     if update_booking.date_to is not None:
#         await BookingDAO.update(id=booking_id, date_to=update_booking.date_to)
#     if update_booking.date_from is not None:
#         await BookingDAO.update(id=booking_id, date_from=update_booking.date_from)
