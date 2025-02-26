from pydantic import BaseModel, EmailStr, Field


class SUserAuth(BaseModel):  # схемы нужны для валидации данных
    """Схема для аутенфикации пользователя"""
    email: EmailStr
    password: str = Field(min_length=8)


class SUserInfo(BaseModel):
    id: int
    email: str
    role: str