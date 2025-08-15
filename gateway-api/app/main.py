from fastapi import FastAPI,APIRouter
from app.routes import api

app=FastAPI()


app.include_router(api.router)
app.include_router(api.router)



