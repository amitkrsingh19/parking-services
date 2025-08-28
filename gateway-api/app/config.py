from pydantic_settings import BaseSettings

#REFRESH_TOKEN_EXPIRATION_TIME = int(os.getenv("REFRESH_TOKEN_EXPIRATION_TIME", 10080))
class Settings(BaseSettings):
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRATION_TIME:int 

    model_Config={
        "env_file" : ".env"
        }

settings = Settings() # type: ignore
    