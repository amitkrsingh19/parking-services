from fastapi import APIRouter,status,Depends
from fastapi.responses import JSONResponse
from app.database import db
from app.dependencies.utils import verify_password
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import auth_handler
from motor.motor_asyncio import AsyncIOMotorCollection 

router=APIRouter(prefix="/login",tags=["login"])

#   User/Admin login Endpoint
@router.post("/")
async def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(),
               user_db:AsyncIOMotorCollection = Depends(db.get_user_collection),
               admin_db:AsyncIOMotorCollection = Depends(db.get_admin_collection)):

    # Find the user by email
    user = await user_db.find_one({"email": user_credentials.username})
    #    If not User look for Admin
    if user is None:
        user=await admin_db.find_one({"email":user_credentials.username})
    if user is None or not user:
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
        "sub": str(user["_id"]),
        "email":user["email"],
        "role": user["role"]
    
    }
    
    # Create the access token
    access_token =auth_handler.create_access_token(payload)

    return {"access_token": access_token, "token_type": "bearer"}
