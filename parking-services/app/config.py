from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_HOSTNAME: str = "localhost"
    DB_PORT: int = 5432
    DB_PASSWORD: str = "password"
    DB_NAME: str = "mydb"
    DB_USERNAME: str = "user"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHMS: str = "HS256"
    ACCESS_TOKEN_EXPIRATION_TIME: int = 30

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }



settings = Settings()
print("Loaded DB Port:", settings.DB_PORT)
