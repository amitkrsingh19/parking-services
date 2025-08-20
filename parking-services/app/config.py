from pydantic_settings import BaseSettings
import socket

#REFRESH_TOKEN_EXPIRATION_TIME = int(os.getenv("REFRESH_TOKEN_EXPIRATION_TIME", 10080))
class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION_TIME: int
    USER_SERVICES_DB: str
    PARKING_SERVICES_DB:str
    MONGO_URI:str

    @property
    def mongo_uri(self) -> str:
        host = "mongo" if self._is_docker() else "localhost"
        return f"mongodb://{host}:27017"

    def _is_docker(self) -> bool:
        try:
            socket.gethostbyname("mongo")
            return True
        except socket.error:
            return False

    model_config={
        "env_file" : ".env",
        "extra":"ignore",
        }

settings = Settings() # type: ignore