#   -----RELATIONAL DATABASE-------
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

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
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

mongodb_client: AsyncIOMotorClient 

async def connect_to_mongo():
    #Connect to MongoDB once at startup.
    global mongodb_client, parking_db,user_db
    mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
    parking_db = mongodb_client[settings.PARKING_SERVICES_DB]
    user_db=mongodb_client[settings.USER_SERVICES_DB]
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    #Close MongoDB connection at shutdown.
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
"""