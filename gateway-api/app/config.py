import os
from dotenv import load_dotenv

#load the enviroment
load_dotenv()

# Authentication / JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "SECRET_KEY")  # fallback if not set
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRATION_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRATION_TIME", 30))  # minutes
#REFRESH_TOKEN_EXPIRATION_TIME = int(os.getenv("REFRESH_TOKEN_EXPIRATION_TIME", 10080))