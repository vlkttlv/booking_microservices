from datetime import date

from sqlalchemy import and_, column, func, insert, select, values
from sqlalchemy.sql.expression import cast
from sqlalchemy import Integer
from hotels_service.db import async_session_maker
from hotels_service.models import Hotels
from hotels_service.rooms.models import Rooms


class HotelDAO():

    model = Hotels

    @classmethod
    async def find_all_by_location_and_date(cls, booked_rooms_data, location: str, services: str,
                                            min_price: int = 0, max_price: int = 100000):
        """Получение всех отелей для указанной локации, дат и ценового диапазона."""

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

        booked_hotels = (
            select(Rooms.hotel_id, Rooms.price, func.sum(
                Rooms.quantity - func.coalesce(booked_rooms.c.rooms_booked, 0)
            ).label("rooms_left"))
            .select_from(Rooms)
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
            .group_by(Rooms.hotel_id, Rooms.price)
            .cte("booked_hotels")
        )

        # SELECT id, name, location, services, rooms_quantity, image_id, hotel_id, hotels.name, SUM(rooms_left) as room_left FROM hotels
        # LEFT JOIN booked_hotels ON booked_hotels.hotel_id = hotels.id
        # WHERE rooms_left > 0 AND location LIKE '%Алтай%'
        # 	AND booked_hotels.price >= 0 AND booked_hotels.price <= 30000
        # 	AND 'Парковка' = ANY(services) AND array['Бассейн'] && CAST(services as text[])
        # GROUP BY id, hotel_id

        input_services = services.split(',')

        get_hotels_with_rooms = (
            select(
                Hotels.__table__.columns,
                cast(func.sum(booked_hotels.c.rooms_left), Integer).label("rooms_left"),
            )
            .join(booked_hotels, booked_hotels.c.hotel_id == Hotels.id, isouter=True)
            .where(
                and_(
                    booked_hotels.c.rooms_left > 0,
                    Hotels.location.like(f"%{location}%"),
                    booked_hotels.c.price >= min_price,
                    booked_hotels.c.price <= max_price,
                    Hotels.services.contains(input_services)

                )
            )
            .group_by(Hotels.id, booked_hotels.c.hotel_id)
        )
        async with async_session_maker() as session:
            hotels_with_rooms = await session.execute(get_hotels_with_rooms)
            return hotels_with_rooms.mappings().all()


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

