from typing import List
from pydantic import BaseModel, Field


class SHotels(BaseModel):
    id: int
    name: str
    location: str
    services: List[str]
    rooms_quantity: int


class SHotelInfo(SHotels):
    rooms_left: int

    class Config:
        from_attributes = True


class SHotelAdd(BaseModel):
    name: str
    location: str
    services: List[str]
    rooms_quantity: int = Field(ge=1)