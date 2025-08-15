from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from app.configs import SECRET_KEY, ALGORITHM,ACCESS_TOKEN_EXPIRATION_TIME
from app.database.db import get_user_collection, get_admin_collection
from bson import ObjectId
from datetime import datetime,timedelta
from typing import Dict


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#   Create Access Token
async def create_access_token(payload:Dict):
    to_encode=payload.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encoded_jwt

#   Verify  Acces Token
async def verify_token(token, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("_id")
        role = payload.get("role")  # store role in token during login
        if sub is None or role is None:
            raise credential_exception
        return sub, role
    except JWTError:
        raise credential_exception

#   get current user from User Collection
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_db=Depends(get_user_collection),
):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sub, role = await verify_token(token, cred_exc)
    if role != "user":
        raise HTTPException(status_code=403, detail="User access only")
    user = user_db.find_one({"_id": ObjectId(sub)})
    if not user:
        raise cred_exc
    return {**user, "role": role}

#   get current admin from Admin Collection
async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    admin_db=Depends(get_admin_collection),
):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sub, role =await verify_token(token, cred_exc)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    admin = admin_db.find_one({"_id": ObjectId(sub)})
    if not admin:
        raise cred_exc
    return {**admin, "role": role}
