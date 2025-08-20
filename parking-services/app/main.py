from fastapi import FastAPI
from app.routes import slots,station
from app.database import db
app=FastAPI()

@app.get("/")
async def root():
    return {"message":"from parking backend"}
@app.on_event("startup")
async def startup_db_client():
    await db.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_mongo_connection()
app.include_router(slots.router)
app.include_router(station.router)


