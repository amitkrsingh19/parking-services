from fastapi import status, Depends,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UserRequest,UpdateUser
from app.dependencies.utils import hash_password
from app.database.db import get_user_collection
from bson import ObjectId
from app.dependencies import auth_handler
from datetime import datetime, timezone
from typing import Any, Dict
from motor.motor_asyncio import AsyncIOMotorCollection 

router=APIRouter(prefix="/users",tags=["users"])

#create new user to the app
@router.post("/")
async def CreateUser(User: UserRequest, 
                    user_db: AsyncIOMotorCollection = Depends(get_user_collection)):
    # Hash the password before saving
    hashed_password = hash_password(User.password)

    user_data = {
        "email": User.email,
        "password": hashed_password,
        "name": User.nme,  
        "role": "user",
        "created_at": datetime.now(timezone.utc),
    }

    # Insert into MongoDB
    result =await user_db.insert_one(user_data)

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

#Role:superadmin,get user by id
@router.get("/{user_id}",dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def get_user(user_id:str,
                   user_db:AsyncIOMotorCollection =Depends(get_user_collection)):
    try:
        user =await user_db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "User not found"})
        
        user_response = {
            "_id": ObjectId(user["_id"]),
            "email": user["email"],
            "name": user["nme"],
            "created_at": user["created_at"].isoformat(),
            "updated_at": user.get("updated_at", None)
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=user_response)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})
#Delete current User
#Role:  User
@router.delete("/",dependencies=[Depends(auth_handler.requires_role("user"))])
async def delete_user(payload:dict=Depends(auth_handler.get_token_payload),
                user_db:AsyncIOMotorCollection=Depends(auth_handler.get_user_collection)):
    #check for the user exists in database
    user_id_from_token=payload.get("sub")
           # Check if a user ID was found in the token
    if not user_id_from_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
            )
    user= await user_db.find_one({"_id":user_id_from_token})
    if user:
        #delete the user
        result=await user_db.delete_one({"_id":user_id_from_token})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or already deleted"
            )
    # Return a 204 No Content for a successful deletion
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content={"message":"user deleted successfully"})

#Role:User, profile
@router.get("/profile/me",dependencies=[Depends(auth_handler.requires_role("user"))])
async def get_profile(user_db:AsyncIOMotorCollection =Depends(get_user_collection),
                current_user:Dict[str, Any]=Depends(auth_handler.get_current_user)):
    user=await user_db.users.find_one({"_id":current_user["_id"]})
    if not user:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,content="user not found")
    user["_id"] = str(user["_id"])
    user.pop("password",None)
    return user

#role:User ,Update profile
@router.patch("/profile/update",dependencies=[Depends(auth_handler.requires_role("user"))])
async def update_user(user:UpdateUser,user_db:AsyncIOMotorCollection =Depends(get_user_collection),
                current_user:Dict[str,Any]=Depends(auth_handler.get_current_user)):
    update_data=user.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["password"]=hash_password(update_data["password"])
    result=await user_db.users.update_one(
        {'_id':ObjectId(current_user["_id"])},
        {'$set':update_data}
    )

    if result.matched_count==0:
        return JSONResponse(status_code=status.HTTP_304_NOT_MODIFIED,content="no updated values")
    return {"message":"profile updated"}


