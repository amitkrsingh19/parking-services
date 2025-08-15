from fastapi import status, Depends,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UserRequest,UpdateUser
from app.auth.utils import hash_password
from app.database.db import get_user_collection
from bson import ObjectId
from app.auth import auth_handler
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

#get user function will be changed according to the use cases
#Role:super admin
@router.get("/")
async def get_users(skip: int = 0, limit: int = 10,user_db: AsyncIOMotorCollection  = Depends(get_user_collection)):
    users_cursor = user_db.users.find({}, {"password": 0}).limit(limit).skip(skip)  # exclude password
    users_list = []
    async for user_doc in users_cursor:
        user_doc["id"] = str(user_doc.pop("_id"))
        # Check if the datetime field exists and convert it to an ISO 8601 string
        if "created_at" in user_doc and isinstance(user_doc["created_at"], datetime):
            user_doc["created_at"] = user_doc["created_at"].isoformat()
            users_list.append(user_doc)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"users": users_list,"skip":skip,"limit":limit}
    )

#Role:superadmin,get user by id
@router.get("/{user_id}")
async def get_user(user_id:str,user_db:AsyncIOMotorCollection =Depends(get_user_collection)):
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

#Role:User, profile
@router.get("/profile/me")
async def get_profile(user_db:AsyncIOMotorCollection =Depends(get_user_collection),
                current_user:Dict[str, Any]=Depends(auth_handler.get_current_user)):
    user=await user_db.users.find_one({"_id":current_user["_id"]})
    if not user:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,content="user not found")
    user["_id"] = str(user["_id"])
    user.pop("password",None)
    return user

#role:User ,Update profile
@router.patch("/profile/update")
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

#role:superadmin ,register new admin
@router.post("/register-admin")
async def create_admin(User: UserRequest,
                       user_db: AsyncIOMotorCollection  = Depends(get_user_collection)):
    # 1. Await the count_documents call
    user_count = await user_db.users.count_documents({})
    
    if user_count == 0:
        role = "superadmin"
    else:
        role = "admin"
    
    # 2. Await the find_one call
    existing_user = await user_db.users.find_one({"email": User.email})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin with this email already exists."
        )
    
    # 3. Hash the password
    hashed_password = hash_password(User.password)
    
    user_data = {
        "email": User.email,
        "password": hashed_password,
        "name": User.nme,  # Corrected key name
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }
    
    # 4. Insert the new user
    await user_db.users.insert_one(user_data)
    
    return {"message": f"'{role}' created successfully."}
