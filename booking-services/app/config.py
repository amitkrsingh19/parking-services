# config.py
import os
from dotenv import load_dotenv
import socket
load_dotenv()

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY","SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRATION_TIME = int(os.getenv("ACCES_TOKEN_EXPIRATION_TIME", "30"))  # minutes
async def get_mongo_uri():
    try:
        socket.gethostbyname("mongo")
        return "mongodb://mongo:27017"
    except socket.error:
        return "mongodb://localhost:27017"
    
# MongoDB Settings
MONGO_URI = f"mongodb://{os.getenv("MONGO_HOST")}:{os.getenv("MONGO_PORT")}"
USER_DB_NAME = os.getenv("USER_DB_NAME","user_services_db")
PARKING_DB_NAME = os.getenv("PARKING_DB_NAME","PARKING_SERVICES_DB")