from sqlalchemy import JSON, Column, ForeignKey, Integer, String, ARRAY
from hotels_service.db import Base


class Rooms(Base):

    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, nullable=False)
    hotel_id = Column(ForeignKey("hotels.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    services = Column(ARRAY(item_type=String), nullable=True)
    quantity = Column(Integer, nullable=False)
