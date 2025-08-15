from fastapi import APIRouter,status,Depends,HTTPException
from pymongo.collection import Collection
from fastapi.responses import JSONResponse
from app.database import db
from app.dependencies.utils import verify_password
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import auth_handler
from motor.motor_asyncio import AsyncIOMotorCollection 

router=APIRouter(prefix="/login",tags=["login"])

#user login
@router.post("/-users")
async def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(),
               user_db:AsyncIOMotorCollection = Depends(db.get_user_collection)):

    # Find the user by email
    user = await user_db.users.find_one({"email": user_credentials.username})
    
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"}
        )

    # Verify the provided password
    if not verify_password(user_credentials.password,user["password"]):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"}
        )

    # Create the payload with the user's role
    payload = {
        "sub": str(user["_id"]),  # Using 'sub' as a standard JWT claim
        "role": user["role"]
    }
    
    # Create the access token
    access_token = await auth_handler.create_access_token(payload)

    return {"access_token": access_token, "token_type": "bearer"}

# Admin Login
@router.post("/-admin")
async def login_admin(admin_credentials: OAuth2PasswordRequestForm = Depends(),
               admin_db:AsyncIOMotorCollection = Depends(db.get_admin_collection)):

    # Find the user by email
    admin = await admin_db.admin.find_one({"email": admin_credentials.username})
    
    if not admin:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"}
        )

    # Verify the provided password
    if not verify_password(admin_credentials.password,admin["password"]):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"}
        )

    # Create the payload with the user's role
    payload = {
        "sub": str(admin["_id"]),
        "email":str(admin),  # Using 'sub' as a standard JWT claim
        "role": admin["role"]
    }
    
    # Create the access token
    access_token = await auth_handler.create_access_token(payload)

    return {"access_token": access_token, "token_type": "bearer"}