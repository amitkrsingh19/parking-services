from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from app.config import SECRET_KEY, ALGORITHM
from app.database.db import get_user_collection, get_admin_collection
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#    Verifying Access Token
async def verify_token(token, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("_id")
        role = payload.get("role")  
        if sub is None or role is None:
            raise credential_exception
        return sub, role
    except JWTError:
        raise credential_exception

#   Get Current User From Database
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_db=Depends(get_user_collection),
):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sub, role =await verify_token(token, cred_exc)
    if role != "user":
        raise HTTPException(status_code=403, detail="User access only")

    user = await user_db.find_one({"_id": ObjectId(sub)})
    if not user:
        raise cred_exc

    return {**user, "role": role}

#   Get Current Admin from Database
async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    admin_db=Depends(get_admin_collection),
):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sub, role = await verify_token(token, cred_exc)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    admin = await admin_db.find_one({"_id": ObjectId(sub)})
    if not admin:
        raise cred_exc
    return {**admin, "role": role}
