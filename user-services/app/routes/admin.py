from fastapi import status, Depends,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UserRequest,UpdateUser
from app.dependencies.utils import hash_password
from app.database.db import get_admin_collection,get_user_collection
from app.dependencies import auth_handler
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection 

router=APIRouter(prefix="/users",tags=["admin"])

#   role:superadmin ,register new admin
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

#   get user function will be changed according to the use cases
#   Role:super admin
@router.get("/",dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def get_users(skip: int = 0, limit: int = 10,
                    user_db: AsyncIOMotorCollection  = Depends(get_user_collection)):
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

#   Role:superadmin,get user by id
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
#   Delete a User
#   Role: Super Admin
@router.delete("/",dependencies=[Depends(auth_handler.requires_role("superadmin"or"admin"))])
async def delete_user(payload:dict=Depends(auth_handler.get_token_payload),
                admin_db:AsyncIOMotorCollection=Depends(get_admin_collection)):
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
#   Role: Superadmin
@router.delete("/{id}",dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def del_admin(current_admin:dict=Depends(auth_handler.get_token_payload),
                    admin_db:AsyncIOMotorCollection = Depends(get_admin_collection)):
    #check for admin in database
    admin_id=current_admin.get("sub")
    admin= await admin_db.find_one({"_id":admin_id})
    if admin:
        await admin_db.delete_one({"_id":admin_id})
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                            content="admin deleted from database")
    else:
        raise  HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)