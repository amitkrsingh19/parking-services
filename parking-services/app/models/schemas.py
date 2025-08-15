from pydantic import BaseModel
from typing import Optional,Dict
from datetime import datetime
from  pydantic.config import ConfigDict

#add slot data
class SlotCreate(BaseModel):
    station_id: str  # Reference to a station
    slot_id:str
    is_available: bool = True
    price_per_hour:int
    charging_support: bool
#slot output
class SlotOut(BaseModel):
    slot_id: str
    station_id: str
    is_available: bool
    charging_support: bool

#admin station input
class stationin(BaseModel):
    station_id:str
    station_name:str
    location:str
    total_slots:int

#station output 
class StationOut(BaseModel):
    station_id: str
    station_name: str
    location: str
    total_slots: int

#past/upcoming booking response
class Dashboard(BaseModel):
    past_booking:Optional[int]
    upcoming_booking:Optional[int]
    total_booking:Optional[int]
    last_booking_info:Optional[Dict]

