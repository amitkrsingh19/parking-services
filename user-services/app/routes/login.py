from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import models 
from app.database import db
from typing import Union
from app.dependencies.utils import verify_password
from app.dependencies.auth_handler import create_access_token

router = APIRouter(tags=["Login"])

@router.post("/login/")
async def login_user(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(db.get_db)
):
    email = user_credentials.username
    password = user_credentials.password

    # Try to find user in Users table
    user = db.query(models.User).filter(models.User.email == email).first()

    # Try to find user in Admins table
    admin = db.query(models.Admin).filter(models.Admin.email == email).first()

    # If not found in either → invalid email
    if not user and not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email credentials")

    # Pick whichever exists (User or Admin)
    db_user: Union[models.User, models.Admin]
    db_user = user if user else admin

    # Verify password
    if not verify_password(password, db_user.password):  # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    # Create JWT token with role info
    token_data = {"sub": db_user.email,"id":db_user.id ,"role": db_user.role} # type: ignore
    access_token = create_access_token(token_data)

    return {"access_token": access_token, "token_type": "bearer"}
