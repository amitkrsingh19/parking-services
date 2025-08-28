from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,DECIMAL,Enum
from sqlalchemy.orm import relationship
from datetime import datetime       
import enum
from app.database.db import Base

#  --------ENUMS---------
class SlotStatus(str,enum.Enum):
    available="available"
    booked="booked"
    cancelled="cancelled"

class SlotType(str,enum.Enum):
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

    # One station → many slots
    slots = relationship("Slot", back_populates="station", cascade="all, delete-orphan")

# ---SLOT TABLE---
class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("station.id", ondelete="CASCADE"), nullable=False)
    slot_number= Column(String,nullable=False)
    slot_type=Column(Enum(SlotType,name='slottype'),nullable=False)
    status = Column(Enum(SlotStatus,name="slotstatus"), default=SlotStatus.available)
    price_per_hour=Column(Integer,nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    admin_id = Column(Integer, nullable=False)

    # Relationship to station
    station = relationship("Parking", back_populates="slots")

    # One slot → many bookings
    bookings = relationship("Booking", back_populates="slot", cascade="all, delete-orphan")

# ---BOOKINGS TABLE---
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,nullable=False)
    slot_id = Column(Integer, ForeignKey("slots.id", ondelete="CASCADE"), nullable=False)
    start_time=Column(DateTime,default=datetime.utcnow)
    end_time=Column(DateTime,nullable=False)
    status = Column(Enum(SlotStatus, name="slotstatus"),default=SlotStatus.booked,nullable=False)
    price=Column(DECIMAL)
    created_at = Column(DateTime, default=datetime.utcnow)

    slot = relationship("Slot", back_populates="bookings")