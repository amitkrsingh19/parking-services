from pydantic_settings import BaseSettings

#REFRESH_TOKEN_EXPIRATION_TIME = int(os.getenv("REFRESH_TOKEN_EXPIRATION_TIME", 10080))
class Settings(BaseSettings):
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRATION_TIME:int 

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings() # type: ignore
    