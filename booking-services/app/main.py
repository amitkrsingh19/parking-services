from fastapi import FastAPI
from app.routes import bookings,admin_booking


app=FastAPI()

@app.get("/")
async def read_root():
    return "hello from booking backend"

app.include_router(bookings.router)
app.include_router(admin_booking.router)