from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from hotels_service.db import Base


class Hotels(Base):

    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(ARRAY(String))
    rooms_quantity = Column(Integer, nullable=False)

