from fastapi import status, Depends,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UserRequest,UpdateUser
from app.dependencies.utils import hash_password
from app.database.db import get_admin_collection,get_user_collection
from app.dependencies import auth_handler
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection 

router=APIRouter(prefix="/admins",tags=["admin"])

#   role:superadmin ,register new admin
@router.post("/create")
async def create_admin(admin: UserRequest,
                       admin_db: AsyncIOMotorCollection = Depends(get_admin_collection)):
    #  Await the count_documents call
    user_count = await admin_db.count_documents({})
    
    if user_count == 0:
        role = "superadmin"
    else:
        role = "admin"
    
    # Await the find_one call
    existing_user = await admin_db.find_one({"email": admin.email})
    
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
        "name": admin.nme,   # fixed typo
        "role": role,
        "created_at": datetime.now(timezone.utc)
    }
    
    # Insert the new user
    await admin_db.insert_one(user_data)
    
    return {"message": f"'{role}' created successfully."}

# Get all users (superadmin only)
@router.get("/all", dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def get_all_users(skip: int = 0, limit: int = 10,
                        user_db: AsyncIOMotorCollection = Depends(get_user_collection)):
    users_cursor = user_db.find({}, {"password": 0}).limit(limit).skip(skip)
    users_list = []
    async for user_doc in users_cursor:
        # Convert ObjectId and datetime to strings for JSON serialization
        user_doc["id"] = str(user_doc.pop("_id"))
        user_doc["created_at"] = user_doc["created_at"].isoformat()
        users_list.append(user_doc)

    return {"users": users_list, "skip": skip, "limit": limit}


# Delete an admin (superadmin only)
@router.delete("/{admin_id}", dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def delete_admin(admin_id: str,
                       admin_db: AsyncIOMotorCollection = Depends(get_admin_collection),
                       current_user: dict = Depends(auth_handler.get_token_payload)):
    try:
        # Ensure a superadmin cannot delete themselves
        if admin_id == current_user.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot delete your own admin account."
            )
        
        result = await admin_db.delete_one({"_id": ObjectId(admin_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found or already deleted.")
        
        return {"message": "Admin deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
