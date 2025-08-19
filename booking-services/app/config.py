from pydantic_settings import BaseSettings
import socket

#REFRESH_TOKEN_EXPIRATION_TIME = int(os.getenv("REFRESH_TOKEN_EXPIRATION_TIME", 10080))
class settings(BaseSettings):
    MONGO_URI:str
    USER_DB_NAME:str
    PARKING_DB_NAME:str
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRATION_TIME:int 

    class config:
        env_file=".env"
def get_mongo_uri():
    try:
        socket.gethostbyname("mongo")
        return "mongodb://mongo:27017"
    except socket.error:
        return "mongodb://localhost:27017"