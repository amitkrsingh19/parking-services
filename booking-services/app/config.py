import os
from dotenv import load_dotenv
import socket
#load the enviroment
load_dotenv()

# Authentication / JWT settings
SECRET_KEY = os.getenv("SECRET_KEY","SECRET_KEY")  # fallback if not set
ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRATION_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRATION_TIME", 30))  # minutes
#REFRESH_TOKEN_EXPIRATION_TIME = int(os.getenv("REFRESH_TOKEN_EXPIRATION_TIME", 10080))

def get_mongo_uri():
    try:
        socket.gethostbyname("mongo")
        return "mongodb://mongo:27017"
    except socket.error:
        return "mongodb://localhost:27017"

MONGO_URI = f"mongodb://mongo:27017"
USER_DB_NAME = os.getenv("USER_DB_NAME","user_services_db")
PARKING_DB_NAME = os.getenv("PARKING_DB_NAME","PARKING_SERVICES_DB")