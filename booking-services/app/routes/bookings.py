from fastapi import APIRouter,Depends,HTTPException,status
from pymongo.collection import Collection
from app.database import db
from app.models import schemas
from motor.motor_asyncio import AsyncIOMotorCollection
from bson.objectid import ObjectId
from fastapi.responses import JSONResponse
from datetime import datetime,timedelta
from app.auth_utils import get_current_user,get_current_admin

router=APIRouter(prefix="/bookings",
                  tags=["bookings"])

#book a slot 
@router.post("/",response_model=schemas.Bookedslot)
async def book_slot(
    booking: schemas.BookSlot,
    current_user: dict = Depends(get_current_user),
    booking_db: AsyncIOMotorCollection = Depends(db.get_booking_collection),
    slot_db: AsyncIOMotorCollection = Depends(db.get_parking_collection)
):
    # Extract user_id from authenticated user
    user_id = current_user

    # Define time range
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=booking.duration)

        #check for conflict,if any:
    conflict = booking_db.find_one({
    "station_id": booking.station_id,
    "slot_id": booking.slot_id,
    "status": "booked",
    # Overlapping condition:
    "$or": [
        {
            "start_time": {"$lt": end_time},
            "end_time": {"$gt": start_time}
        }
    ]
})

    if conflict:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": "Slot already booked for this time range"}
        )
    # Check if slot exists & available
    slot = await slot_db.find_one({"slot_id": booking.slot_id,"is_available":True})
    if not slot:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Slot ID not found in database"})
    #update the slot is_available to false #we will introduce web-socket soon
    await slot_db.update_one({"slot_id": booking.slot_id},{"$set":{"is_available":False}})
    # Insert new booking
    new_booking=booking.dict()
    new_booking["user_id"]=user_id
    new_booking["amount_paid"]=(slot["price_per_hour"]) * booking.duration
    new_booking["status"]="Booked"
    new_booking["start_time"]=start_time
    new_booking["end_time"]=end_time
    await booking_db.insert_one(new_booking)
    return new_booking

#user booking history
@router.get("/history")
async def user_bookings(
    booking_db: AsyncIOMotorCollection= Depends(db.get_booking_collection),
    current_user: str = Depends(get_current_user),
):
    try:
        # Find all bookings for the current user
        book_cursor= booking_db.find({"user_id": current_user}).sort("start_time", -1)
        booked = []

        async for doc in book_cursor:
            doc["_id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            doc["start_time"] = doc["start_time"].isoformat()
            doc["end_time"] = doc["end_time"].isoformat()
            booked.append(doc)

        return JSONResponse(status_code=status.HTTP_200_OK, content=booked)

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

#user booking dashboard
@router.get("/user/dashboard", response_model=schemas.UserDashboard)
async def user_dashboard(
    current_user: dict = Depends(get_current_user),
    booking_db: Collection = Depends(db.get_booking_collection)
):
    try:
        user_id =current_user
        # Ensure ObjectId type
        now = datetime.utcnow()

        # 1. Count past bookings (ended before now)
        past_booking = booking_db.count_documents({
            "user_id": user_id,
            "end_time": {"$lt": now}
        })

        # 2. Count active/upcoming bookings
        upcoming_booking = booking_db.count_documents({
            "user_id": user_id,
            "end_time": {"$gte": now}
        })

        # 3. Total bookings
        total_booking = booking_db.count_documents({
            "user_id": user_id
        })

        # 4. Get most recent booking
        last_booking_info = booking_db.find_one(
            {"user_id": user_id},
            sort=[("start_time", -1)]  # Latest by start time
        )

        if last_booking_info:
            last_booking_info["_id"] = str(last_booking_info["_id"])
            last_booking_info["user_id"] = str(last_booking_info["user_id"])
            last_booking_info["start_time"] = last_booking_info["start_time"].isoformat()
            last_booking_info["end_time"] = last_booking_info["end_time"].isoformat()

        # Response payload
        dashboard = {
            "past_booking": past_booking,
            "upcoming_booking": upcoming_booking,
            "total_booking": total_booking,
            "last_booking_info": last_booking_info
        }

        return dashboard

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#cancelling the booking
@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: str,
    booking_db: Collection = Depends(db.get_booking_collection),
    current_user: str = Depends(get_current_user),
    slot_db: Collection = Depends(db.get_parking_collection)
):
    try:
        obj = ObjectId(booking_id)

        # Step 1: Find and delete the booking
        booking = await booking_db.find_one_and_delete({"_id": obj})
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking ID not found",
                headers={"message": "Please enter a valid booking ID"}
            )

        # Step 2: Update slot availability using slot_id from booking record
        await slot_db.find_one_and_update(
            {"slot_id": booking["slot_id"]},
            {"$set": {"is_available": True}}
        )

        # Optional: Clean up ObjectId before returning
        booking["_id"] = str(booking["_id"])
        booking["user_id"] = str(booking["user_id"])
        booking["start_time"] = booking["start_time"].isoformat()
        booking["end_time"] = booking["end_time"].isoformat()

        return {"message": "Booking cancelled", "booking": booking}

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@router.get("/")
def get_booking(charging_support:bool,booking_db:Collection=Depends(db.get_booking_collection),
                current_user:str=Depends(get_current_user)):
    booking_db.find({""})
