from pydantic import BaseModel
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Enum,DECIMAL
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime       
import enum
from app.database.db import Base



#  --------ENUMS----------
class UserRole(enum.Enum):
    user= "user"
    admin="admin"
    superadmin="superadmin"

class SlotStatus(enum.Enum):
    available="available"
    booked="booked"
    cancelled="cancelled"

# ---USER TABLE---
class User(Base):
    __tablename__="users"

    id = Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True,index=True)
    phone=Column(String,nullable=True,unique=True,index=True)
    password=Column(String,nullable=False)
    role=Column(Enum(UserRole),default=UserRole.user)
    created_at=Column(DateTime,default=datetime.utcnow)

class Admin(Base):
    __tablename__="admin"

    id = Column(Integer,primary_key=True,index=True)
    name=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True,index=True)
    phone=Column(String,nullable=True,unique=True,index=True)
    password=Column(String,nullable=False)
    role=Column(Enum(UserRole),default=UserRole.admin)
    created_at=Column(DateTime,default=datetime.utcnow)
