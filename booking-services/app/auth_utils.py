from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from fastapi import Depends,HTTPException,status
from app.config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRATION_TIME


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

#user access
def get_current_user(token:str=Depends(oauth2_scheme)):
    credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail="COULD NOT VALIDATE CREDENTIALS",headers={"WWW-AUTHENTICATE":"BEARER"})
    
    return verify_user_token(token,credential_exception)

#verify admin token
def verify_admin_token(token,credential_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,ALGORITHM)
        admin_id=payload.get("_id")
        if admin_id is None:
            raise credential_exception
        
    except JWTError:
        raise credential_exception
    return admin_id

#admin access
def get_current_admin(token:str=Depends(oauth2_scheme)):
        credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                       detail="COULD NOT VALIDATE CREDENTIALS",
                                       headers={"WWW-AUTHENTICATE":"BEARER"})
        return verify_admin_token(token,credential_exception)