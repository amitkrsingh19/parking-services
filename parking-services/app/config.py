from pydantic_settings  import BaseSettings

class Settings(BaseSettings):
    DB_HOSTNAME: str
    DB_PORT: int
    DB_PASSWORD: str
    DB_NAME: str
    DB_USERNAME: str
    SECRET_KEY: str
    ALGORITHMS: str
    ACCESS_TOKEN_EXPIRATION_TIME:int =30

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings() #type: ignore

print("Loaded DB Port:", settings.DB_PORT)
print("Loaded DB Password:", settings.DB_PASSWORD)
