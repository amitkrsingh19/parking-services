from fastapi import FastAPI
from app.routes import slots,station
from app.database.db import Base, engine

app=FastAPI()

@app.get("/")
async def root():
    return {"message":"from parking backend"}

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(slots.router)
app.include_router(station.router)


