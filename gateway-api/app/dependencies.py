from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from pydantic import EmailStr
from datetime import datetime,timezone,timedelta
from fastapi import Depends,HTTPException,status
from app.config import ACCESS_TOKEN_EXPIRATION_TIME,SECRET_KEY,ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#create role based access token
def create_access_token(sub:str,email:EmailStr,role:str):
    to_encode= {"_id":sub,"email":email,"role":role,"exp":datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME) }
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

#get token payload
def get_token_payload(token,credential_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credential_exception

# role-checker dependency
def requires_role(required_role: str):
    def role_checker(payload: dict = Depends(get_token_payload)):
        if payload.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource"
            )
        return payload
    return role_checker