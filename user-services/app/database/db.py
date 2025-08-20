from motor.motor_asyncio import AsyncIOMotorClient
from app.configs import settings
from typing import Optional

# Global variables with type hints
mongodb_client: Optional[AsyncIOMotorClient] = None
user_db = None


async def connect_to_mongo():
    global mongodb_client, user_db
    try:
        mongodb_client = AsyncIOMotorClient(settings.mongo_uri)
        user_db = mongodb_client[settings.USER_SERVICES_DB]
        print(f"✅ Connected to MongoDB. Databases: {user_db.name}")

    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        mongodb_client = None


async def close_mongo_connection():
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("❌ MongoDB connection closed.")


# Collection getters for the user database
def get_user_collection():
    if user_db is None:
        raise RuntimeError("User database not initialized. Call connect_to_mongo() first.")
    return user_db.get_collection("users")


def get_admin_collection():
    if user_db is None:
        raise RuntimeError("User database not initialized. Call connect_to_mongo() first.")
    return user_db.get_collection("admins")
