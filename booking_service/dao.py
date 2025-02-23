from datetime import date
from fastapi import HTTPException
from sqlalchemy import ARRAY, Integer, String, and_, column, func, insert, or_, select, update, values, delete, select
from sqlalchemy.exc import SQLAlchemyError
from booking_service.models import Bookings
from booking_service.db import async_session_maker


class BookingDAO():

    model = Bookings

    @classmethod
    async def get_booked_rooms(cls, date_from: date, date_to: date):
        """
        Находит все забронированные комнаты на заданный период
        
        -Аргументы:
            date_from: Дата начала брони
            date_to: Дата конца брони
        """
        booked_rooms = (
            select(Bookings.room_id, Bookings.price, func.count(Bookings.room_id).label("rooms_booked"))
            .select_from(Bookings)
            .where(
                or_(
                    and_(
                        Bookings.date_from >= date_from,
                        Bookings.date_from <= date_to,
                    ),
                    and_(
                        Bookings.date_from <= date_from,
                        Bookings.date_to > date_from,
                    ),
                ),
            )
            .group_by(Bookings.room_id, Bookings.price)
        )
        async with async_session_maker() as session:
            res_booked_rooms = await session.execute(booked_rooms)
            return res_booked_rooms.mappings().all()

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
    async def find_all(cls, rooms_data, user_id: int):
        """
        Находит все брони пользователя
        
        -Аргументы:
            rooms_data: Список всех комнат
            user_id: ID пользователя
        """
        
        """Cоздание временной таблицы rooms"""
        rooms_values = values(
            column('id', Integer),
            column('hotel_id', Integer),
            column('name', String),
            column('description', String),
            column('services', ARRAY(item_type=String)),
            column('price', Integer),
            column('quantity', Integer)
        ).data([(item['id'], item['hotel_id'],
                 item['name'], item['description'],
                 item['services'], item['price'],
                 item['quantity']) for item in rooms_data]).alias('rooms_values')

        rooms = (
            select(
                rooms_values.c.id,
                rooms_values.c.hotel_id,
                rooms_values.c.name,
                rooms_values.c.description,
                rooms_values.c.services,
            )
            .select_from(rooms_values)
            .cte('rooms')
        )

        # SELECT *
        # FROM  bookings  b left JOIN  rooms r ON b.room_id = r.id
        # where b.user_id = 3;
        # -- 3 = user_id

        query = (
            select(
                Bookings.__table__.columns,
                rooms.c.hotel_id,
                rooms.c.name,
                rooms.c.description,
                rooms.c.services,
            )
            .join(rooms, rooms.c.id == Bookings.room_id, isouter=True)
            .where(Bookings.user_id == user_id)
        )
        async with async_session_maker() as session:
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def add(cls, rooms_data, user_id: int, room_id: int, date_from: date, date_to: date):
        """Добавление бронирования, если есть свободные комнаты
        
        - Аргументы:
            rooms_data: список комнат
            user_id: ID пользователя
            room_id: ID комнаты
            date_from: Дата заезда
            date_to: Дата выезда
        """
        try:
            async with async_session_maker() as session:
                # WITH booked_rooms AS (
                #     SELECT * FROM bookings
                #     WHERE room_id = 1 AND
                #     (date_from >= '2024-06-25' AND date_from <= '2024-07-05') OR
                #     (date_from <= '2024-06-25' AND date_to >= '2024-06-25' )
                # )
                booked_rooms = select(Bookings).where(
                    and_(Bookings.room_id == room_id,
                         or_(
                             and_(Bookings.date_from >= date_from,
                                  Bookings.date_from <= date_to),
                             and_(Bookings.date_from <= date_from,
                                  Bookings.date_to > date_from)
                         )
                         )
                ).cte('booked_rooms')

                # -- получаем все забронированные комнаты + их количесвто всего
                # -- select * from rooms
                # -- left join booked_rooms on rooms.id = booked_rooms.room_id
                # -- where rooms.id = 1

                rooms_values = values(
                        column('id', Integer),
                        column('hotel_id', Integer),
                        column('name', String),
                        column('description', String),
                        column('services', ARRAY(item_type=String)),
                        column('price', Integer),
                        column('quantity', Integer)
                    ).data([(item['id'], item['hotel_id'],
                            item['name'], item['description'],
                            item['services'], item['price'],
                            item['quantity']) for item in rooms_data]).alias('rooms_values')

                rooms = (
                        select(
                            rooms_values.c.id,
                            rooms_values.c.hotel_id,
                            rooms_values.c.name,
                            rooms_values.c.description,
                            rooms_values.c.services,
                            rooms_values.c.price,
                            rooms_values.c.quantity,
                        )
                        .select_from(rooms_values)
                        .cte('rooms')
                    )
                
                # Подсчет забронированных комнат
                booked_count_query = select(func.count()).select_from(booked_rooms).scalar_subquery()

                # Количество свободных комнат
                free_rooms_query = select(rooms.c.quantity - booked_count_query).filter(rooms.c.id == room_id)
                result = await session.execute(free_rooms_query)

                free_rooms: int = result.scalar()
                if free_rooms > 0:
                    get_price = select(rooms.c.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()

                    add_booking = insert(Bookings).values(
                        room_id=room_id,
                        user_id=user_id,
                        date_from=date_from,
                        date_to=date_to,
                        price=price
                    ).returning(Bookings)  # возвращает вставленную строку

                    new_booking = await session.execute(add_booking)
                    await session.commit()
                    return new_booking.scalar()
                else:
                    return None
        except (SQLAlchemyError, Exception) as e:  # эта конструкция отловит ВСЕ ошибки
            # динамически формируем сообщение для логера
            msg = str(e)
            if isinstance(e, SQLAlchemyError):
                msg = "Databasw Exc: Cannot add booking"
            if isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"
            raise HTTPException(status_code=400, detail=msg)


    @classmethod
    async def update(cls, id: int, **data):
        """
        Обновляет запись

        -Аргументы:
            id: ID записи, которую надо обновить
            **data: атрибуты модели в качестве ключей и их значения в качестве значений.
        """
        async with async_session_maker() as session:
            stmt = update(cls.model).where(cls.model.id == id).values(**data)
            await session.execute(stmt)
            await session.commit()


    @classmethod
    async def delete(cls, **filter_by):
        '''
        Удаляет запись из БД
        '''
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)
            await session.execute(query)
            await session.commit()
