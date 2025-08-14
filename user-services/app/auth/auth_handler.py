from fastapi import APIRouter,status,Depends,HTTPException
from pymongo.collection import Collection
from datetime import datetime,timedelta
from jose import jwt,JWTError
from app.configs import ACCESS_TOKEN_EXPIRATION_TIME,SECRET_KEY,ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from bson.objectid import ObjectId
from app.database.db import get_user_collection

routers=APIRouter(prefix="/login",tags=["login"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")    
#create users access tken
async def create_access_token(data:dict):
    to_encode=data.copy()
    #calculate expiration time
    expire=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)

    to_encode.update({"exp":expire.timestamp()})

    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt
#verifying access token
async def verify_token(token,credential_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload.get("_id")
        if user_id is None:
            raise credential_exception
        
    except JWTError:
        raise credential_exception
    return user_id


async def get_current_user(token:str=Depends(oauth2_scheme),user_db:Collection=Depends(get_user_collection)):
    credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail="COULD NOT VALIDATE CREDENTIALS",headers={"WWW-AUTHENTICATE":"BEARER"})
    id,role=await verify_token(token,credential_exception)
    user=user_db.find_one({"_id":ObjectId(str(id))},{"role":role})
    return user