from aioredis import Redis
import requests
from datetime import date, datetime
from fastapi import Depends, HTTPException, Query, Request, Path
from typing import List, Optional
from fastapi import APIRouter
from hotels_service.dao import HotelDAO
from hotels_service.db import get_redis
from hotels_service.exceptions import IncorrectRoleException, WrongDateFrom
from hotels_service.rooms.dao import RoomDAO
from hotels_service.rooms.schemas import SRoom, SRoomAdd, SRoomInfo
from hotels_service.schemas import SHotelAdd, SHotelInfo, SHotels
from ast import literal_eval


router = APIRouter(prefix="/hotels", tags=["Отели"])
api_router = APIRouter(prefix="/api/hotels", tags=["for others apis"])


@router.get("/{location}", response_model=List[SHotelInfo],
            summary="Return hotels for specified params")
async def get_hotels(
    date_from: date = Query(default=datetime.now().date(),
                            description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(default=datetime.now().date(),
                          description=f"Например, {datetime.now().date()}"),
    location: str = Path(description="Введите название города или отеля"),
    services: str = Query(default="Парковка", description="Вводите услуги через запятую"),
    min_price: int = 0, max_price: int = 100_000,
    redis: Redis = Depends(get_redis)
):
    """Получение всех отелей для указанной локации, дат, ценового диапазона и услуг"""
    if date_from >= date_to:
        raise WrongDateFrom
    
    cache_key = f'{location}{date_from}{date_to}{services}{min_price}{max_price}'
    result = await redis.get(cache_key)

    # Если данные отсутствуют в кэше, выполняем запрос и сохраняем результат в Redis
    if result is None:
        booked_rooms = requests.get(f'http://127.0.0.1:8002/api/bookings/all/?date_from={date_from}&date_to={date_to}',
                            headers={'accept':'application/json'})
        result = await HotelDAO.find_all_by_location_and_date(booked_rooms.json(), location, services, min_price, max_price)
        await redis.set(f'{location}{date_from}{date_to}{services}{min_price}{max_price}', str(result), ex=20) # Сохраняем результат в кэше на 20 секунд
    else:
        result = literal_eval(result)
    return result


@router.post("/add_hotel")
async def add_hotel(hotel_data: SHotelAdd, request: Request):
    """Добавление отеля. Доступно только администраторам"""

    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    if response.json()['role'] != 'admin':
        raise IncorrectRoleException

    new_hotel_id = await HotelDAO.add(
        name=hotel_data.name,
        location=hotel_data.location,
        services=hotel_data.services,
        rooms_quantity=hotel_data.rooms_quantity,
    )

    return {"detail": f"Отель с ID {new_hotel_id} был успешно добавлен в БД"}


@router.get("/{hotel_id}/rooms", response_model=List[SRoomInfo],
            summary="Return the list of available rooms in the hotel")
async def get_rooms(hotel_id: int,
                    date_from: date = Query(default=datetime.now().date(),
                                            description=f"Например, {datetime.now().date()}"),
                    date_to: date = Query(default=datetime.now().date(),
                                          description=f"Например, {datetime.now().date()}"),
                    min_check: int = 0,
                    max_check: int = 100_000):
    """Получение списка свободных комнат в отеле"""
    booked_rooms = requests.get(f'http://127.0.0.1:8002/api/bookings/all/?date_from={date_from}&date_to={date_to}',
                                headers={'accept':'application/json'})
    return await RoomDAO.find_all_rooms(booked_rooms.json(), hotel_id, date_from, date_to, min_check, max_check)


@router.post("/{hotel_id}/add_room")
async def add_room(room_data: SRoomAdd, request: Request):
    """Добавление комнаты в БД. Доступно только администраторам"""
    access_token = request.cookies.get("booking_access_token")
    headers = {'accept': 'application/json', 'token': access_token}
    response = requests.get('http://127.0.0.1:8000/auth/me', headers=headers)
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Not authorized")
    if response.json()['role'] != 'admin':
        raise IncorrectRoleException
    
    new_room_id = await RoomDAO.add(hotel_id=room_data.hotel_id,
                                    name=room_data.name,
                                    description=room_data.description,
                                    services=room_data.services,
                                    quantity=room_data.quantity,
                                    price=room_data.price)

    return {"detail": f"Комната с ID {new_room_id} была успешно добавлена в БД"}

@api_router.get("/", response_model=List[SHotels],
                summary="Returns a list of hotels")
async def get_all_hotels():
    """Возвращает список всех отелей"""
    hotels = await HotelDAO.find_all()
    return hotels

@api_router.get("/rooms", response_model=List[SRoom],
                summary="Returns a list of rooms")
async def get_all_rooms():
    """Возвращает список всех комнат"""
    rooms = await RoomDAO.find_all()
    return rooms

@api_router.get("/rooms/{room_id}")
async def get_room_by_id(room_id: int) -> Optional[SRoom]:
    """Возвращает информацию о комнате по ID.
    Просто находит запись в БД, не учитывая, свободна ли эта комната или нет"""
    return await RoomDAO.find_one_or_none(id=room_id)

@api_router.get("/{hotel_id}", summary="Returns the hotel by ID")
async def get_hotel_by_id(hotel_id: int) -> Optional[SHotels]:
    """Вовзращает информацию об отеле по ID.
    Находит запись в БД, не учитывая, есть ли в отеле свободные комнаты или нет"""
    return await HotelDAO.find_one_or_none(id=hotel_id)


# @router.post("/add-hotels-and-rooms-in-db", summary="Добавление записей в БД")
# async def add_hotels_and_rooms_in_db():
    
#     with open("hotels_service/data/hotels.json", 'r', encoding="utf-8") as file:
#         hotels_data = json.load(file)  # Загружаем данные из JSON
#         for hotel in hotels_data:
#             await HotelDAO.add(name=hotel['name'],
#                                location=hotel['location'],
#                                services=hotel['services'],
#                                rooms_quantity=hotel['rooms_quantity'])
            
#     with open("hotels_service/data/rooms.json", 'r', encoding="utf-8") as file:
#         rooms_data = json.load(file)  # Загружаем данные из JSON
#         for room in rooms_data:
#             await RoomDAO.add(hotel_id=room['hotel_id'],
#                               name=room['name'],
#                               description=room['description'],
#                               price=room['price'],
#                               services=room['services'],
#                               quantity=room['quantity'])
#     return {"detail": 'отели и комнаты были добавлены в БД'}