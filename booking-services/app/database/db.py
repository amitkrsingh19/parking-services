from pymongo import MongoClient
from pymongo.collection import Collection
from app.config import PARKING_DB_NAME,USER_DB_NAME,get_mongo_uri
from motor.motor_asyncio import AsyncIOMotorClient


# Mongo client
client = AsyncIOMotorClient("localhost",27017)

if not PARKING_DB_NAME or not USER_DB_NAME:
    raise RuntimeError("PARKING_SERVICES_DB and USER_SERVICES_DB must be set")


# Access DBs
parking_db = client[PARKING_DB_NAME]
user_db = client[USER_DB_NAME]

# parking-slot Collections
async def get_slot_collection():
    return parking_db["parking_slots"]
#booking-slot colletions
async def get_booking_collection():
    return parking_db["parking_bookings"]
#get station collection
async def get_station_collection():
    return parking_db["parking_stations"]
#user collection
async def get_user_collection():
    return user_db["users"]
