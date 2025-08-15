# In your parking-services/app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer,HTTPBearer,HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# This dependency verifies the token and returns the payload
def get_token_payload(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credential_exception

# This dependency checks for a required role
def requires_role(required_role: str):
    def role_checker(payload: dict = Depends(get_token_payload)):
        if payload.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource"
            )
        return payload
    return role_checker