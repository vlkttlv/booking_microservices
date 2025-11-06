import jwt
from typing import Annotated
from fastapi import APIRouter, Depends, Header, Request, Response
from users_service.auth import authenticate_user, create_access_token, create_refresh_token, get_password_hash
from users_service.dao import RefreshTokenDAO, UsersDAO
from users_service.dependencies import get_current_user, get_refresh_token
from users_service.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from users_service.schemas import SUserAuth, SUserInfo
from users_service.config import settings
from users_service.exceptions import IncorrectTokenFormatException
from logger import logger

router = APIRouter(
    prefix="/auth",
    tags=["Аутенфикация и пользователи"]
)


@router.post("/register", status_code=201)
async def register_user(user_data: SUserAuth):
    """Функция, регистрирующая пользователя"""
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.add(email=user_data.email, hashed_password=hashed_password, role="user")
    logger.info("Пользователь зарегистрировался")


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    """Функция позволяет пользователю авторизоваться"""
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = await create_refresh_token({"sub": str(user.id), "role": user.role})
    response.set_cookie("booking_access_token", access_token, httponly=True)
    logger.info(f"Пользователь {user.email} залогинился")
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/logout")
async def logout_user(response: Response, current_user=Depends(get_current_user)):
    """Функция, с помощью которой пользователь выходит из системы. Удаляет действующую куку"""
    response.delete_cookie("booking_access_token")
    await RefreshTokenDAO.delete(user_id=current_user.id)  # удаляем refresh токен


@router.get("/me", response_model=SUserInfo, summary="Returns info about the user")
async def get_user_info(request: Request, token: Annotated[str | None, Header()] = None):
    """Метод, возвращающий информацию о пользователе(id, email, пароль и роль)"""
    if not token:
        token = request.cookies.get("booking_access_token")
    current_user = get_current_user(token)
    return await current_user


@router.post("/token/refresh", summary="Updates the access token")
async def refresh_token(response: Response, refresh: str = Depends(get_refresh_token)):
    """Обновление access токена с помощью refresh токена"""
    try:
        payload = jwt.decode(refresh, settings.SECRET_KEY, settings.ALGORITHM)
        user_id: str = payload.get("sub")
        role = payload.get("role")
        if user_id is None:
            raise IncorrectTokenFormatException
    except Exception as e:
        raise IncorrectTokenFormatException from e
    new_access_token = create_access_token({"sub": user_id, "role": role})
    response.set_cookie("booking_access_token", new_access_token, httponly=True)
    logger.info(f"Токен был обновлен для юзера: {user_id} {role}")
    return {"access_token": new_access_token}
