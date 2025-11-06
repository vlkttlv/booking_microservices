from pydantic import EmailStr
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from users_service.config import settings
from users_service.dao import RefreshTokenDAO, UsersDAO
from users_service.exceptions import IncorrectEmailOrPasswordException
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def get_password_hash(password: str) -> str:
    """Генерирует хэшированный пароль"""
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    """Проверяет пароль на валидность"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Создает токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM
    )
    return encode_jwt


async def create_refresh_token(data: dict) -> str:
    """Создает refresh токен"""
    to_encode = data.copy()
    now_time = datetime.utcnow()
    expire = now_time + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    user_id = int(data["sub"])

    # Проверяем, есть ли уже такой refresh токен в БД
    token_user = await RefreshTokenDAO.find_one_or_none(user_id=user_id)
    if not token_user:
        await RefreshTokenDAO.add(token=token, user_id=user_id, created_at=now_time, expires_at=expire)
    else:
        await RefreshTokenDAO.update_token(created_at=now_time, expires_at=expire, user_id=user_id, token=token)
    return token


async def authenticate_user(email: EmailStr, password: str):
    """Аутенфицирует пользователя, возвращает либо его, либо ошибку"""
    user = await UsersDAO.find_one_or_none(email=email)
    if not (user and verify_password(password, user.hashed_password)):
        raise IncorrectEmailOrPasswordException
    return user
