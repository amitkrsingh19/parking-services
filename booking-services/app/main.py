from fastapi import FastAPI
from app.routes import bookings,admin_booking
from app.database import db

app=FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await db.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_mongo_connection()
@app.get("/")
async def read_root():
    return "hello from booking backend"

app.include_router(bookings.router)
app.include_router(admin_booking.router)