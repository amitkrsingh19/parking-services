import socket
from pydantic_settings import BaseSettings


async def get_mongo_uri():
    try:
        socket.gethostbyname("mongo")
        return "mongodb://mongo:27017"
    except socket.error:
        return "mongodb://localhost:27017"
    
class settings(BaseSettings):
    MONGO_URI:str
    USER_DB_NAME:str
    PARKING_DB_NAME:str
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRATION_TIME:int 

    class config:
        env_file=".env"
# MongoDB Settings
#MONGO_URI = f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}"
#USER_DB_NAME = os.getenv('USER_DB_NAME','user_services_db')
#PARKING_DB_NAME = os.getenv('PARKING_DB_NAME','PARKING_SERVICES_DB')