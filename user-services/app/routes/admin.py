from fastapi import status, Depends,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UserRequest,UpdateUser
from app.auth.utils import hash_password
from app.database.db import get_admin_collection
from app.auth import auth_handler
from datetime import datetime, timezone
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorCollection 

router=APIRouter(prefix="/users",tags=["users"])

#role:superadmin ,register new admin
@router.post("/register-admin")
async def create_admin(admin: UserRequest,
                       admin_db: AsyncIOMotorCollection = Depends(get_admin_collection)):
    #  Await the count_documents call
    user_count = await admin_db.admin.count_documents({})
    
    if user_count == 0:
        role = "superadmin"
    else:
        role = "admin"
    
    # Await the find_one call
    existing_user = await admin_db.admin.find_one({"email": admin.email})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin with this email already exists."
        )
    
    # Hash the password
    hashed_password = hash_password(admin.password)
    
    user_data = {
        "email": admin.email,
        "password": hashed_password,
        "name": admin.nme,  # Corrected key name
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }
    
    # Insert the new user
    await admin_db.admin.insert_one(user_data)
    
    return {"message": f"'{role}' created successfully."}

#delete admin for database
@router.delete("/{id}")
async def del_admin(current_admin:str=Depends(auth_handler.get_current_admin),
                    admin_db:AsyncIOMotorCollection = Depends(get_admin_collection)):
    #check for admin in database
    admin= await admin_db.admin.find_one({"_id":current_admin})
    if admin:
        await admin_db.admin.delete_one({"_id":current_admin})
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                            content="admin deleted from database")
    else:
        raise  HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)