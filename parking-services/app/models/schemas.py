from pydantic import BaseModel
from typing import Optional,Dict
import enum
from datetime import datetime

#  --------ENUMS---------
class SlotStatus(str,enum.Enum):
    available="available"
    booked="booked"
    cancelled="cancelled"

class SlotType(str,enum.Enum):
    car="car"
    bike="bike"
    ev="ev"

#add slot data
class SlotCreate(BaseModel):
    station_id : int
    slot_number: str
    slot_type:SlotType
    status : SlotStatus

    class config:
        orm_mode=True
    
#slot output
class SlotOut(BaseModel):
    station_id : int
    slot_number: str
    slot_type:SlotType
    status : SlotStatus
    admin_id:int

    class config:
        orm_mode=True
# show slots to the user
class SlotShow(BaseModel):
    station_id:int
    slot_id:str
    location:str
    slot_number:str
    slot_type:SlotType
    status:SlotStatus

    class config:
        orm_mode=True
#admin station input
class StationIn(BaseModel):
    station_name:str
    location:str
    capacity:int

    class config:
        orm_mode=True

#station output 
class StationOut(BaseModel):
    station_id: str
    station_name: str
    location: str
    capacity: int

    class config:
        orm_mode=True

#past/upcoming booking response
class Dashboard(BaseModel):
    past_booking:Optional[int]
    upcoming_booking:Optional[int]
    total_booking:Optional[int]
    last_booking_info:Optional[Dict]

#   BOOKING SERVICES SCEHMAS
# take bookings
class BookSlot(BaseModel):
    station_id:str
    slot_number:str
    duration:int


# booking response 
class Bookedslot(BookSlot):
    price:int
    status:str
    start_time:datetime
    end_time:datetime

#input to deleted booking
class DelBooking(BaseModel):
    slot_id:str
    station_id:str

#past/upcoming booking response
class UserDashboard(BaseModel):
    past_bookings:Optional[int]
    upcoming_bookings:Optional[int]
    total_bookings:Optional[int]
    last_booking_info:Optional[Dict]

#past/upcoming booking response
class AdminDashboard(BaseModel):
    past_bookings:Optional[int]
    upcoming_bookings:Optional[int]
    future_bookings:Optional[Dict]
    last_booking_info:Optional[Dict]

