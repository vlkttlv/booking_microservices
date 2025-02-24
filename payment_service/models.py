from payment_service.db import Base
from sqlalchemy import Column, Date, Integer, ForeignKey, String


class Payments(Base):
    """Класс, описывающий модель оплаты"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))
    booking_id = Column(ForeignKey("bookings.id"))
    amount = Column(Integer, nullable=False)
    date_to = Column(Date, nullable=False)
    status = Column(String)
