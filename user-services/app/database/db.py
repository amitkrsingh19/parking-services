from motor.motor_asyncio import AsyncIOMotorClient
from app.configs import MONGO_URI, USER_DB_NAME

mongodb_client: AsyncIOMotorClient | None = None
database = None

async def connect_to_mongo():
    global mongodb_client, database
    mongodb_client = AsyncIOMotorClient(MONGO_URI)
    database = mongodb_client[USER_DB_NAME]
    print(f"✅ Connected to MongoDB @ {MONGO_URI}")

async def close_mongo_connection():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("❌ MongoDB connection closed")
        
# Collection getters
def get_user_collection():
    if database is None:
        raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
    return database["users"]

#def get_station_collection():
 #   if database is None:
  #      raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
   # return database["stations"]

#def get_parking_collection():
 #   if database is None:
  #      raise RuntimeError("Database connection not initialized. Call connect_to_mongo() first.")
   # return database["parking"]
