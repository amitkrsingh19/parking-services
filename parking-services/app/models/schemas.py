from pydantic import BaseModel
from typing import Optional,Dict
import enum

#  --------ENUMS---------
class SlotStatus(enum.Enum):
    available="available"
    booked="booked"
    cancelled="cancelled"

class SlotType(enum.Enum):
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

