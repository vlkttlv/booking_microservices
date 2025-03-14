from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь уже существует"


class IncorrectEmailOrPasswordException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверная почта или пароль"


class IncorrectRoleException(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Вы не являетесь админом"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class TokenExpiredException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"


class TokenAbsentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен отсутствует"


class IncorrectTokenFormatException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверный формат токена"


class UserIsNotPresentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED


class RoomCannotBeBooked(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не осталось свободных мест"


class WrongDateFrom(BookingException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Дата заезда не должна быть позже даты выезда"


class BookingAlreadyPaid(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Данное бронирование уже оплачено"


class IncorrectBookingID(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Некорректный ID бронирования"