from fastapi import status, Depends,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UserRequest,UpdateUser
from app.dependencies.utils import hash_password
from app.database.db import get_user_collection,get_admin_collection
from bson import ObjectId
from app.dependencies import auth_handler
from datetime import datetime, timezone
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorCollection 

router=APIRouter(prefix="/users",tags=["users"])

#create new user to the app
@router.post("/")
async def CreateUser(user: UserRequest, 
                    user_db: AsyncIOMotorCollection = Depends(get_user_collection)):
    # Hash the password before saving
    hashed_password = hash_password(user.password)

    user_data = {
        "email": user.email,
        "password": hashed_password,
        "name": user.nme,   # fixed typo: nme -> name
        "role": "user",
        "created_at": datetime.now(timezone.utc),
    }

    # Insert into MongoDB
    result = await user_db.insert_one(user_data)

    # Prepare safe return data
    user_return = {
        "email": user_data["email"],
        "name": user_data["name"],
        "created_at": user_data["created_at"].isoformat()
    }

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=user_return
    )

# Get a single user by ID (superadmin only)
@router.get("/{user_id}", dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def get_user_by_id(user_id: str,
                         user_db: AsyncIOMotorCollection = Depends(get_user_collection)):
    try:
        user = await user_db.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user["_id"] = str(user["_id"])
        user["created_at"] = user["created_at"].isoformat()
        if user.get("updated_at"):
            user["updated_at"] = user["updated_at"].isoformat()
            
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
# Delete a user by ID (superadmin only)
@router.delete("/{user_id}", dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def delete_user(user_id: str,
                      user_db: AsyncIOMotorCollection = Depends(get_user_collection),
                      admin_db: AsyncIOMotorCollection = Depends(get_admin_collection)):
    try:
        # Check if the user to be deleted exists
        user_to_delete = await user_db.find_one({"_id": ObjectId(user_id)})
        if not user_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        # Delete the user
        result = await user_db.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or already deleted.")
        
        return {"message": "User deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Delete user self (user)
@router.delete("/",dependencies=[Depends(auth_handler.requires_role("user"))])
async def delete_user_self(payload:dict=Depends(auth_handler.get_token_payload),
                user_db:AsyncIOMotorCollection=Depends(get_user_collection)):
    user_id_from_token = payload.get("sub")
    if not user_id_from_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
        )
    try:
        oid = ObjectId(user_id_from_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id in token")

    user = await user_db.find_one({"_id": oid})
    if user:
        result = await user_db.delete_one({"_id": oid})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or already deleted"
            )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content={"message":"user deleted successfully"})

#Role:User, profile
@router.get("/profile/me",dependencies=[Depends(auth_handler.requires_role("user"))])
async def get_profile(user_db:AsyncIOMotorCollection =Depends(get_user_collection),
                current_user:Dict[str, Any]=Depends(auth_handler.get_token_payload)):
    user_id = current_user.get("sub")
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id in token")
    user = await user_db.find_one({"_id": oid})
    if not user:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,content="user not found")
    user["_id"] = str(user["_id"])
    user.pop("password",None)
    return user

#Update profile (Users)
@router.patch("/profile/update",dependencies=[Depends(auth_handler.requires_role("user"))])
async def update_user(user:UpdateUser,
                      user_db:AsyncIOMotorCollection =Depends(get_user_collection),
                current_user:dict=Depends(auth_handler.get_token_payload)):
    update_data=user.dict(exclude_unset=True)
    user_id=current_user.get("sub")
    try:
        oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id in token")

    if "password" in update_data:
        update_data["password"]=hash_password(update_data["password"])
    result=await user_db.update_one(
        {'_id':oid},
        {'$set':update_data}
    )

    if result.matched_count==0:
        return JSONResponse(status_code=status.HTTP_304_NOT_MODIFIED,content="no updated values")
    return {"message":"profile updated"}