from fastapi import APIRouter, Depends, Response
from users_service.auth import authenticate_user, create_access_token, get_password_hash
from users_service.dao import UsersDAO
from users_service.dependencies import get_current_user
from users_service.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from users_service.models import Users
from users_service.schemas import SUserAuth


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
    return {"access_token": access_token, "role": user.role}


@router.post("/logout")
async def logout_user(response: Response):
    """Функция, с помощью которой пользователь выходит из системы. Удаляет действующую куку"""
    response.delete_cookie("booking_access_token")


@router.get("/me")
async def read_user_me(current_user: Users = Depends(get_current_user)):
    """Метод, возвращающий информацию о пользователе(id, email, пароль и роль)"""
    return current_user