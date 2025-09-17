from pydantic import BaseModel,validator
import re
from typing import Optional
from pydantic import EmailStr

#request schemas for user
class UserCreate(BaseModel):
    email:EmailStr
    password:str
    name:str
    phone: Optional[str] = None
#   To validate phone number from user
    @validator("phone")
    def validate_phone(cls, v):
        # allow empty/None phone (optional)
        if v is None or v == "":
            return v
        if not re.match(r'^\+?\d{10,15}$', v):
            raise ValueError("Invalid phone number format")
        return v

#request schemas for UserLogin
class UserLogin(BaseModel):
    email:EmailStr
    password:str

class TokenData(BaseModel):
    _id:Optional[int]

#to update user
class UpdateUser(BaseModel):
    name:Optional[str]
    email:Optional[EmailStr]
    password:Optional[str]
    phone:Optional[str]