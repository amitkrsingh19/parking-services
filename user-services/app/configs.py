from pydantic_settings import BaseSettings
import socket

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION_TIME: int
    USER_SERVICES_DB: str
    MONGO_URI: str | None = None  

    def _is_docker(self) -> bool:
        try:
            socket.gethostbyname("mongo")
            return True
        except socket.error:
            return False

    @property
    def mongo_uri(self) -> str:
        # prefer env var if provided (set in docker-compose)
        if self.MONGO_URI:
            return self.MONGO_URI
        host = "mongo" if self._is_docker() else "localhost"
        return f"mongodb://{host}:27017"

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

settings = Settings() # type: ignore
