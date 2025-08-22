from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from app.configs import settings
from datetime import datetime,timedelta
from typing import Dict,Any


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

#   Create Access Token
def create_access_token(data:Dict[str,Any])->str:
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_TIME)
    to_encode.update({"exp":expire})
    #Convert Enum to Json serializable
    for k, v in to_encode.items():
        if hasattr(v, "value"):  # If Enum
            to_encode[k] = v.value

    encoded_jwt=jwt.encode(to_encode,settings.SECRET_KEY,settings.ALGORITHMS)
    return encoded_jwt

#get token payload
def get_token_payload(token:str=Depends(oauth2_scheme))->Dict[str,Any]:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHMS])
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
