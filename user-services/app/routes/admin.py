from fastapi import status, Depends,APIRouter,HTTPException
from sqlalchemy.orm import Session
from app.models import models,schemas
from app.dependencies.utils import hash_password
from app.database import db
from app.dependencies import auth_handler
from datetime import datetime
from sqlalchemy import func


router=APIRouter(prefix="/admins",tags=["admin"])

#   role:superadmin ,register new admin
@router.post("/create")
async def create_admin(admin: schemas.UserCreate,
                       db: Session = Depends(db.get_db)):
    #  Await the count_documents call
    user_count = db.query(func.count(models.Admin.id)).scalar()
    
    if user_count == 0:
        role = "superadmin"
    else:
        role = "admin"
    
    #   Look for email exist, if any
    existing_user = db.query(models.Admin).filter(models.Admin.email == admin.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin with this email already exists."
        )
    
    # Hash the password
    hashed_password = hash_password(admin.password)
    admin.password= hashed_password
    
    # Insert the new user
    new_admin=models.Admin(**admin.dict())
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"message": f"'{role}' created successfully."}

# Get all users (superadmin only)
@router.get("/all", dependencies=[Depends(auth_handler.requires_role("superadmin"))])
def get_all_users(skip: int = 0, limit: int = 10,
                        db: Session = Depends(db.get_db)):
    # look for all  the user in Database
    users = db.query(models.Admin).offset(skip).limit(limit).all()
    # make a list of users
    users_list = []
    for user in users:
        user_dict = user.__dict__.copy()
        user_dict.pop("password", None)
        user_dict["id"] = str(user_dict.get("id"))
        if "created_at" in user_dict and isinstance(user_dict["created_at"], datetime):
            user_dict["created_at"] = user_dict["created_at"].isoformat()
        users_list.append(user_dict)

    return {"users": users_list, "skip": skip, "limit": limit}


# Delete an admin (superadmin only)
@router.delete("/{admin_id}", dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def delete_admin(admin_id: int,
                       db: Session = Depends(db.get_db),
                       current_user: dict = Depends(auth_handler.get_token_payload)):
    try:
        # Ensure a superadmin should not get deleted 
        if admin_id == current_user.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot delete your own admin account."
            )
        
        result = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
        if result == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found or already deleted.")
    
        db.delete(result)
        db.commit()
        return {"message": "Admin deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
