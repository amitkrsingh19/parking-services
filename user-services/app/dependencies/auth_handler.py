from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from app.configs import SECRET_KEY, ALGORITHM,ACCESS_TOKEN_EXPIRATION_TIME
from bson import ObjectId
from datetime import datetime,timedelta
from typing import Dict,Any


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")
#   Create Access Token
def create_access_token(data:Dict[str,Any])->str:
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt

#get token payload
def get_token_payload(token:str=Depends(oauth2_scheme))->Dict[str,Any]:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credential_exception
# role-checker dependency
def requires_role(required_role: str):
    def role_checker(payload: Dict[str, Any] = Depends(get_token_payload)):
        if payload.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource"
            )
        return payload
    return role_checker
