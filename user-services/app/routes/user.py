from fastapi import status, Depends,APIRouter,HTTPException
from fastapi.responses import JSONResponse
from app.models import models ,schemas
from app.dependencies.utils import hash_password
from app.database import db
from sqlalchemy.orm import Session
from app.dependencies import auth_handler
from typing import Any, Dict

router=APIRouter(prefix="/users",tags=["users"])

#create new user to the app
@router.post("/")
async def CreateUser(user: schemas.UserCreate, 
                    db: Session = Depends(db.get_db)):
    # Hash the password before saving
    hashed_password = hash_password(user.password)

    user.password=hashed_password

    # Insert into MongoDB
    new_user=models.User(**user.dict())

    user_return = user.dict()
    user_return.pop("password", None)  # Remove password from response
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=user_return
    )

# Get a single user by ID (superadmin only)
@router.get("/{user_id}", dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def get_user_by_id(user_id: str,
                         db: Session = Depends(db.get_db)):
    try:
        # check for user exist in database
        user = db.query(models.User).filter(models.User._id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user_dict = user.__dict__.copy()
        user_dict["_id"] = user_dict["_id"]
        user_dict["phone"]=user_dict["phone"]
        user_dict.pop("password", None)
        user_dict["created_at"] = user_dict["created_at"].isoformat()
        if user_dict.get("updated_at"):
            user_dict["updated_at"] = user_dict["updated_at"].isoformat()
            
        return user_dict
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
# Delete a user by ID (superadmin only)
@router.delete("/{user_id}", dependencies=[Depends(auth_handler.requires_role("superadmin"))])
async def delete_user(user_id:int,
                      db: Session = Depends(db.get_db)):
    try:
        # Check if the user to be deleted exists
        user_to_delete = db.query(models.User).filter(models.User.id == user_id).first()
        if not user_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        # Delete the user from database
        result = db.query(models.User).filter(models.User.id == user_id).delete(synchronize_session=False)
        if result is None:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or already deleted.")
        
        db.commit()
        return {"message": "User deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Delete user self (user)
@router.delete("/",dependencies=[Depends(auth_handler.requires_role("user"))])
async def delete_user_self(payload:dict=Depends(auth_handler.get_token_payload),
                db: Session = Depends(db.get_db)):
    user_id_from_token = payload.get("sub")
    if not user_id_from_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID not found in token"
        )
    try:
        oid = user_id_from_token
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id in token")

    user = db.query(models.User).filter(models.User.id == oid ).first()
    if user:
        result = db.query(models.User).filter(models.User.id == oid ).delete(synchronize_session=False)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or already deleted"
            )
        db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                        content={"message":"user deleted successfully"})

#Role:User, profile
@router.get("/profile/me",dependencies=[Depends(auth_handler.requires_role("user"))])
async def get_profile(db: Session = Depends(db.get_db),
                current_user:Dict[str, Any]=Depends(auth_handler.get_token_payload)):
    user_id = current_user.get("sub")
    try:
        oid = user_id
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id in token")
    user =  db.query(models.User).filter(models.User.id==oid).first()
    if not user:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,content="user not found")
    user_data=user.__dict__
    user_data.pop("password",None)
    return user_data

#Update profile (Users)
@router.patch("/profile/update", dependencies=[Depends(auth_handler.requires_role("user"))])
def update_user(
    user_update_data: schemas.UpdateUser,
    db: Session = Depends(db.get_db),
    current_user: Dict[str, Any] = Depends(auth_handler.get_token_payload)
):
    update_data = user_update_data.dict(exclude_unset=True)
    user_id = current_user.get("sub")

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="No updated values provided."
        )

    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
    
    # Get the user to update
    user_to_update = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
        
    # Update the model instance with the new data
    for key, value in update_data.items():
        setattr(user_to_update, key, value)
    
    # Commit the changes to the database
    db.commit()
    return {"message": "Profile updated"}