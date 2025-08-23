from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Boolean,Enum
from sqlalchemy.orm import relationship
from datetime import datetime       
import enum
from app.database.db import Base

#  --------ENUMS---------
class SlotStatus(enum.Enum):
    available="available"
    booked="booked"
    cancelled="cancelled"

class SlotType(enum.Enum):
    car="car"
    bike="bike"
    ev="ev"


# ---STATION TABLE---
class Parking(Base):
    __tablename__="station"

    id = Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    location=Column(String,nullable=False,index=True)
    capacity=Column(Integer,nullable=True,index=True)
    created_at=Column(DateTime,default=datetime.utcnow)
    admin_id=Column(Integer,nullable=False)


# ---SLOT TABLE---
class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("station.id", ondelete="CASCADE"), nullable=False)
    slot_number= Column(String,nullable=False)
    slot_type=Column(Enum(SlotType))
    status = Column(Enum(SlotStatus), default=SlotStatus.available)
    created_at = Column(DateTime, default=datetime.utcnow)
    admin_id = Column(Integer, nullable=False)

    station = relationship("Parking", back_populates="slots")