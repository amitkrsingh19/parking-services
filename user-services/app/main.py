from fastapi import FastAPI
from app.routes import user, login, admin 
from app.database.db import Base, engine
from app.models.models import User,Admin  

app = FastAPI(version="1.0.0")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(login.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the User Service API"}
