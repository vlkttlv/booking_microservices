from booking_service.db import Base
from sqlalchemy import Column, Computed, Date, Integer, ForeignKey, String
from sqlalchemy.orm import relationship


class Bookings(Base):
    """Класс, описывающий модель бронирований"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    room_id = Column(ForeignKey("rooms.id"))
    user_id = Column(ForeignKey("users.id"))
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)
    total_cost = Column(Integer, Computed("(date_to-date_from) * price"))
    total_days = Column(Integer, Computed("date_to - date_from"))
    payment_status = Column(String, default="not paid")


class BookedRooms(Base):
    """Забронированные комнаты"""
    __tablename__ = "booked_rooms"
    room_id = Column(Integer, primary_key=True)
    price = Column(Integer)
    rooms_booked = Column(Integer)
