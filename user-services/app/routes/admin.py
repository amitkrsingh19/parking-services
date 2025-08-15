from fastapi import status, Depends,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UserRequest,UpdateUser
from app.dependencies.utils import hash_password
from app.database.db import get_admin_collection
from app.dependencies import auth_handler
from datetime import datetime, timezone
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorCollection 

router=APIRouter(prefix="/users",tags=["users"])

#role:superadmin ,register new admin
@router.post("/register-admin",
             dependencies=[Depends(auth_handler.requires_role("superadmin"or"admin"))])
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

#Delete a User
#Role: Super Admin
@router.delete("/",dependencies=[Depends(auth_handler.requires_role("superadmin"or"admin"))])
async def delete_user(payload:dict=Depends(auth_handler.get_token_payload),
                admin_db:AsyncIOMotorCollection=Depends(auth_handler.get_admin_collection)):
    #check for the user exists in database
    user_id_from_token=payload.get("sub")
           # Check if a user ID was found in the token
    if not user_id_from_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
            )
    user= await admin_db.find_one({"_id":user_id_from_token})
    if user:
        #delete the user
        result=await admin_db.delete_one({"_id":user_id_from_token})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or already deleted"
            )
    # Return a 204 No Content for a successful deletion
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content={"message":"user deleted successfully"})


#delete admin from database
@router.delete("/{id}",dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def del_admin(current_admin:str=Depends(auth_handler.get_current_admin),
                    admin_db:AsyncIOMotorCollection = Depends(get_admin_collection)):
    #check for admin in database
    admin= await admin_db.find_one({"_id":current_admin})
    if admin:
        await admin_db.delete_one({"_id":current_admin})
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                            content="admin deleted from database")
    else:
        raise  HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)