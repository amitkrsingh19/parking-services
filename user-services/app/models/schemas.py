from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pydantic import EmailStr

#request schemas for user
class UserRequest(BaseModel):
    email:EmailStr
    password:str
    nme:str

#request schemas for UserLogin
class UserLogin(BaseModel):
    email:EmailStr
    password:str

class TokenData(BaseModel):
    _id:Optional[int]

#to update user
class UpdateUser(BaseModel):
    nme:Optional[str]
    email:Optional[EmailStr]
    password:Optional[str]