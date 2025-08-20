from fastapi import FastAPI
from .routes import user,login,admin 
from .database import db

app = FastAPI(version="1.0.0")

@app.on_event("startup")
async def startup_db_client():
    await db.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_mongo_connection()

app.include_router(user.router)
app.include_router(login.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the User Service API"}


    


