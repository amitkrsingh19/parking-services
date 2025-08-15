from fastapi import FastAPI,APIRouter,requests,Request,status,HTTPException,Depends
import api
from config import SECRET_KEY,ALGORITHM
from jose import jwt,JWTError
from httpx import AsyncClient

app=FastAPI()


app.include_router(api.router)
app.include_router(api.router)



