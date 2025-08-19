from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

mongodb_client: AsyncIOMotorClient | None = None
user_database = None
parking_database=None

async def connect_to_mongo():
    global mongodb_client, database
    mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
    user_database = mongodb_client[settings.USER_DB_NAME]
    parking_database=mongodb_client[settings.PARKING_DB_NAME]
    print(f"✅ Connected to MongoDB @ {settings.MONGO_URI}")

async def close_mongo_connection():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("❌ MongoDB connection closed")


# Collection getters
def get_user_collection():
    if user_database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return user_database["users"]
def get_admin_collection():
    if user_database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return user_database["users"]
def get_station_collection():
    if parking_database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return parking_database["parking_stations"]

def get_parking_collection():
    if parking_database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return parking_database["parking_slots"]

def get_booking_collection():
    if parking_database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return parking_database["parking_bookings"]
