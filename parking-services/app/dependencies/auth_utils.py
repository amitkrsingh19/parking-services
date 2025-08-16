from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from fastapi import Depends,HTTPException,status
from app.config import SECRET_KEY,ALGORITHM
from typing import Dict,Any
from datetime import datetime,timedelta


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#get token payload
def get_token_payload(token:str=Depends(oauth2_scheme))->Dict[str,Any]:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
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