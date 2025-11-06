from datetime import datetime
from fastapi import Depends, HTTPException, Request
import jwt
from jwt import PyJWTError

from users_service.dao import RefreshTokenDAO, UsersDAO
from users_service.exceptions import IncorrectTokenFormatException, TokenAbsentException, TokenExpiredException, UserIsNotPresentException
from users_service.config import settings


def get_token(request: Request):
    """Метод, получающий текущий токен"""
    token = request.cookies.get("booking_access_token")
    if not token:
        raise TokenAbsentException
    return token


async def get_refresh_token(token: str = Depends(get_token)):
    """Метод, получающий refresh токен"""
    # декодируем текущий access токен без проверки подписи и времени
    try:
        payload = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
    except Exception as e:
        raise IncorrectTokenFormatException from e
    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
    # находим refresh токен для текущего пользователя
    refresh_user = await RefreshTokenDAO.find_one_or_none(user_id=int(user_id))
    # если refresh токен просрочен, то выбрасываем исключение
    if datetime.utcnow().timestamp() > refresh_user.expires_at.timestamp():
        raise HTTPException(status_code=401)
    refresh_token = refresh_user.token
    return refresh_token



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
