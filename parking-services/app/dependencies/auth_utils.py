from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from fastapi import Depends,HTTPException,status
from app.config import SECRET_KEY,ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#verifying token
def verify_user_token(token,credential_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,ALGORITHM)
        user_id=payload.get("_id")
        if user_id is None:
            raise credential_exception
        
    except JWTError:
        raise credential_exception
    return user_id

#get token payload
def get_token_payload(token,credential_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
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

