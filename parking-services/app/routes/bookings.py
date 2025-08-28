from fastapi import APIRouter, Depends, HTTPException
from typing import cast
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import db
from app.dependencies import auth_utils
from app.models.models import Booking, Slot
from app.models.schemas import BookSlot, Bookedslot, UserDashboard
from app.models.schemas import SlotStatus

router = APIRouter(prefix="/bookings", tags=["bookings"])

# ------------------------------
# Book a slot (user role)
# ------------------------------
@router.post("/", dependencies=[Depends(auth_utils.requires_role("user"))], response_model=Bookedslot)
def book_slot(
    booking: BookSlot,
    payload: dict = Depends(auth_utils.get_token_payload),
    db: Session = Depends(db.get_db)
):
    user_id = payload.get("sub")

    # Define booking start and end times
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=booking.duration)

    # Fetch the slot from DB and check if available
    slot_obj = db.query(Slot).filter(
        Slot.station_id == booking.station_id,
        Slot.slot_number == booking.slot_number,
        Slot.status == SlotStatus.available
    ).first()

    if not slot_obj:
        raise HTTPException(status_code=404, detail="Slot not found or not available")

    # Check for overlapping bookings for this slot
    conflict = db.query(Booking).filter(
        Booking.slot_id == slot_obj.id,
        Booking.status == SlotStatus.booked,
        Booking.start_time < end_time,
        Booking.end_time > start_time
    ).first()

    if conflict:
        raise HTTPException(status_code=409, detail="Slot already booked for this time range")

    # Mark slot as booked
    slot_obj["status"] = SlotStatus.booked
    db.commit()

    # Create booking record
    new_booking = Booking(
        user_id=user_id,
        slot_id=slot_obj.id,
        start_time=start_time,
        end_time=end_time,
        status=SlotStatus.booked,
        price=slot_obj.price_per_hour * booking.duration  # Assuming Slot has price_per_hour
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking

# ------------------------------
# User booking history
# ------------------------------
@router.get("/history", dependencies=[Depends(auth_utils.requires_role("user"))])
def user_bookings(
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    user_id = payload.get("sub")
    bookings = db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.start_time.desc()).all()
    return bookings

# ------------------------------
# User dashboard
# ------------------------------
@router.get("/user/dashboard", dependencies=[Depends(auth_utils.requires_role("user"))], response_model=UserDashboard)
def user_dashboard(
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    user_id = payload.get("sub")
    now = datetime.utcnow()

    past_count = db.query(Booking).filter(
        Booking.user_id == user_id,
        Booking.end_time < now
    ).count()

    upcoming_count = db.query(Booking).filter(
        Booking.user_id == user_id,
        Booking.end_time >= now
    ).count()

    total_count = db.query(Booking).filter(
        Booking.user_id == user_id
    ).count()

    last_booking = db.query(Booking).filter(
        Booking.user_id == user_id
    ).order_by(Booking.start_time.desc()).first()

    return {
        "past_bookings": past_count,
        "upcoming_bookings": upcoming_count,
        "total_bookings": total_count,
        "last_booking_info": last_booking
    }

# ------------------------------
# Cancel booking
# ------------------------------
@router.delete("/{booking_id}", dependencies=[Depends(auth_utils.requires_role("user"))])
def cancel_booking(
    booking_id: int,
    db: Session = Depends(db.get_db)
):
    booking_obj = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking_obj:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Free up the slot
    slot_obj = db.query(Slot).filter(Slot.id == booking_obj.slot_id).first()
    if slot_obj:
        slot_obj["status"] = SlotStatus.available

    # Delete the booking
    db.delete(booking_obj)
    db.commit()

    return {"message": "Booking cancelled", "booking_id": booking_id}
