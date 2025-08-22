from fastapi import APIRouter,status,Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import db
from app.models import models,schemas
from app.dependencies.utils import verify_password
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import auth_handler
 

router=APIRouter(prefix="/login",tags=["login"])

#   User/Admin login Endpoint
@router.post("/")
async def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(),
               db: Session = Depends(db.get_db)):

    # Find the user by email
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if user is None or not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"}
        )

    # Verify the provided password
    if not verify_password(user_credentials.password,user.password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid credentials"}
        )

    # Create the payload with the user's role
    payload = {
        "sub": user.id,
        "email":user.email,
        "role": user.role.value
    
    }
    
    # Create the access token
    access_token =auth_handler.create_access_token(payload)

    return {"access_token": access_token, "token_type": "bearer"}
