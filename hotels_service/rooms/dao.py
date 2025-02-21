from datetime import date
from sqlalchemy import Integer, and_, column, func, insert, or_, select, values

from hotels_service.rooms.models import Rooms
from hotels_service.db import async_session_maker

class RoomDAO():

    model = Rooms

    @classmethod
    async def find_all_rooms(cls, booked_rooms_data, hotel_id: int, date_from: date,
                             date_to: date, min_check: int = 0, max_check: int = 100):
        # создание временной таблицы booked_rooms
        booked_rooms_values = values(
            column('room_id', Integer),
            column('rooms_booked', Integer)
        ).data([(item['room_id'], item['rooms_booked']) for item in booked_rooms_data]).alias('booked_rooms_values')

        booked_rooms = (
            select(
                booked_rooms_values.c.room_id,
                booked_rooms_values.c.rooms_booked
            )
            .select_from(booked_rooms_values)
            .cte('booked_rooms')
        )


        get_rooms = (select(
            Rooms.__table__.columns,
            (Rooms.price * (date_to - date_from).days).label("total_cost"),
            (Rooms.quantity - func.coalesce(booked_rooms.c.rooms_booked, 0)
                ).label("rooms_left"),
        )
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
            .where(
            Rooms.hotel_id == hotel_id,
            Rooms.price >= min_check,
            Rooms.price <= max_check,
        ))

        async with async_session_maker() as session:
            rooms = await session.execute(get_rooms)
            return rooms.mappings().all()

    @classmethod
    async def add(cls, **data):
        '''
        Добавляет запись в БД
        '''
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            res = await session.execute(query)
            await session.commit()  # фиксирует изменения в БД, обязательно
            new_id = res.scalar()  # Получаем id новой записи
            return new_id  # Возвращаем id
        

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        '''
        Находит одну запись в БД c условиями
        '''
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        

    
    @classmethod
    async def find_all(cls, **filter_by):
        '''
        Находит все записи в БД, соответствующие условиям
        '''
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(
                **filter_by)  # select * from bookigs
            result = await session.execute(query)
            return result.scalars().all()  # result.mappings().all()