from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class IncorrectRoleException(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Вы не являетесь админом"


class UserIsNotPresentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED

class RoomCannotBeBooked(BookingException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Не осталось свободных мест"


class WrongDateFrom(BookingException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Дата заезда не должна быть позже даты выезда"


class HotelNotFound(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Отель не найден"


class RoomNotFound(BookingException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Комната не найдена"