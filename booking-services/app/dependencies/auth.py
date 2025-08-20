# In your parking-services/app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer,HTTPBearer,HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings
from typing import Dict,Any

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/login")

    #get token payload
def get_token_payload(token:str=Depends(oauth2_scheme))->Dict[str,Any]:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},)
    try:
        payload=jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
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