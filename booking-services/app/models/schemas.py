from pydantic import BaseModel
from typing import Optional,Dict
from datetime import datetime
from  pydantic.config import ConfigDict



#to take bookings
class BookSlot(BaseModel):
    station_id:str
    slot_id:str
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

