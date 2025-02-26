from datetime import datetime
from fastapi import Depends, Request
import jwt
from jwt import PyJWTError

from users_service.dao import UsersDAO
from users_service.exceptions import IncorrectTokenFormatException, TokenAbsentException, TokenExpiredException, UserIsNotPresentException
from users_service.config import settings


def get_token(request: Request):
    """Метод, получающий текущий токен"""
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)):
    """Возвращает пользователя"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except PyJWTError as e:
        raise IncorrectTokenFormatException from e
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        raise TokenExpiredException
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user
