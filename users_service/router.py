from typing import Annotated
from fastapi import APIRouter, Header, Request, Response
from users_service.auth import authenticate_user, create_access_token, get_password_hash
from users_service.dao import UsersDAO
from users_service.dependencies import get_current_user
from users_service.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from users_service.schemas import SUserAuth, SUserInfo


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
    await UsersDAO.add(email=user_data.email, hashed_password=hashed_password)


@router.post("/login")
async def login_user(response: Response, user_data: SUserAuth):
    """Функция позволяет пользователю авторизоваться"""
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)
    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(response: Response):
    """Функция, с помощью которой пользователь выходит из системы. Удаляет действующую куку"""
    response.delete_cookie("booking_access_token")


@router.get("/me", response_model=SUserInfo, summary="Returns info about the user")
async def get_user_info(request: Request, token: Annotated[str | None, Header()] = None):
    """Метод, возвращающий информацию о пользователе(id, email, пароль и роль)"""
    if not token:
        token = request.cookies.get("booking_access_token")
    current_user = get_current_user(token)
    return await current_user
