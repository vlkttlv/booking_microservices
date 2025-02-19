from sqlalchemy import Column, Integer, String
from users_service.db import Base


class Users(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String)
    hashed_password = Column(String)
    role = Column(String, nullable=True, default='user')
