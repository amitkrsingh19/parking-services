from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

mongodb_client: AsyncIOMotorClient 

async def connect_to_mongo():
    """Connect to MongoDB once at startup."""
    global mongodb_client, parking_db,user_db
    mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
    parking_db = mongodb_client[settings.PARKING_SERVICES_DB]
    user_db=mongodb_client[settings.USER_SERVICES_DB]
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    """Close MongoDB connection at shutdown."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("❌ MongoDB connection closed")

# Collection getters
def get_user_collection():
    if user_db is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return user_db["users"]

def get_station_collection():
    if parking_db is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return parking_db["parking_stations"]

def get_parking_collection():
    if parking_db is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return parking_db["parking_slots"]
