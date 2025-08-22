#   -----RELATIONAL DATABASE-------
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.configs import settings

# -----POSTGRE SQL database------------
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}"

engine=create_engine(SQLALCHEMY_DATABASE_URL,echo=True)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()

#dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#   ---- Non Relational Database (Mongodb)
"""

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

"""