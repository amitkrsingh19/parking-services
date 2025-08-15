from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI,USER_DB_NAME

mongodb_client: AsyncIOMotorClient 
database = None

async def connect_to_mongo():
    """Connect to MongoDB once at startup."""
    global mongodb_client, database
    mongodb_client = AsyncIOMotorClient(MONGO_URI)
    database = mongodb_client[USER_DB_NAME]
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    """Close MongoDB connection at shutdown."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("❌ MongoDB connection closed")

# Collection getters
def get_user_collection():
    if database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return database["users"]

def get_station_collection():
    if database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return database["parking_stations"]

def get_parking_collection():
    if database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return database["parking_slots"]
