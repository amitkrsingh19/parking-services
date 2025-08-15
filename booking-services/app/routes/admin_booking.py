from fastapi import APIRouter,Depends,HTTPException,status
from motor.motor_asyncio import AsyncIOMotorCollection
from app.database import db
from app.models import schemas
from app import auth_utils
from datetime import datetime,timedelta

router=APIRouter(prefix="/bookings/admin",tags=["admin booking"])

#admin get their booking of slots they posted
@router.get("/")
async def get_booking(
    booking_db: AsyncIOMotorCollection = Depends(db.get_booking_collection),
    current_user: str = Depends(auth_utils.get_current_user),
    station_db: AsyncIOMotorCollection = Depends(db.get_station_collection)
):
    # Find admin's station
    admin_station = await station_db.find_one({"posted_by": current_user})
    if not admin_station:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="No station found - admin should add station first"
        )

    # Find all bookings for that station
    booking_cursor = booking_db.find({"station_id": admin_station["_id"]})

    # Collect results asynchronously
    bookings = []
    async for doc in booking_cursor:
        bookings.append(doc)

    return bookings

#admin dashboard
@router.get("/dashboard")
async def get_dashboard(
    booking_db: AsyncIOMotorCollection = Depends(db.get_booking_collection),
    slot_db: AsyncIOMotorCollection = Depends(db.get_booking_collection),
    current_user: str = Depends(auth_utils.get_current_user),
    station_db: AsyncIOMotorCollection = Depends(db.get_station_collection)
):
    now = datetime.utcnow()

    # Get admin's station
    admin_station = await station_db.find_one({"posted_by": current_user})
    if not admin_station:
        raise HTTPException(status_code=404, detail="No station found")

    station_id = admin_station["_id"]

    # SLOT STATS 
    total_slots = await slot_db.count_documents({"station_id": station_id})
    available_slots = await slot_db.count_documents({"station_id": station_id, "is_available": True})

    # ---- BOOKING STATS ----
    past_booking_count = await booking_db.count_documents({
        "station_id": station_id,
        "end_time": {"$lt": now}
    })

    upcoming_booking_count = await booking_db.count_documents({
        "station_id": station_id,
        "start_time": {"$gte": now}
    })

    active_booking_count = await booking_db.count_documents({
        "station_id": station_id,
        "start_time": {"$lte": now},
        "end_time": {"$gte": now}
    })

    # ---- REVENUE FROM PAST BOOKINGS ----
    revenue_pipeline = [
        {"$match": {
            "station_id": station_id,
            "end_time": {"$lt": now}
        }},
        {"$group": {
            "_id": None,
            "total_revenue": {"$sum": "$amount_paid"}  
        }}
    ]
    revenue_result = await booking_db.aggregate(revenue_pipeline).to_list(length=1)
    total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0

    return {
        "station_id": str(station_id),
        "slots": {
            "total": total_slots,
            "available": available_slots
        },
        "bookings": {
            "past": past_booking_count,
            "upcoming": upcoming_booking_count,
            "active": active_booking_count
        },
        "revenue": total_revenue
    }

