from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database import db
from app.dependencies import auth_utils
from app.models import models ,schemas

router = APIRouter(prefix="/bookings/admin", tags=["admin booking"])

# ------------------------------
# Get bookings for admin's stations
# ------------------------------
@router.get("/", dependencies=[Depends(auth_utils.requires_role("admin"))])
def get_booking(
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    user_id = payload.get("sub")

    # Get stations posted by admin
    admin_station = db.query(models.Parking).filter(models.Parking.admin_id == user_id).first()
    if not admin_station:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="No station found - admin should add station first"
        )

    # Get all bookings for that station by joining booking and station table
    bookings = db.query(models.Booking).join(models.Slot,models.Slot.id== models.Booking.slot_id ,isouter=True ).group_by(models.Booking.id).all()

    return bookings


# ------------------------------
# Admin dashboard
# ------------------------------
@router.get("/dashboard", dependencies=[Depends(auth_utils.requires_role("admin"))])
def get_dashboard(
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    user_id = payload.get("sub")
    now = datetime.utcnow()

    # Get admin's station
    admin_station = db.query(models.Parking).filter(models.Parking.admin_id == user_id).first()
    if not admin_station:
        raise HTTPException(status_code=404, detail="No station found")
    
    station_id = admin_station.id

    # SLOT STATS
    total_slots = db.query(models.Slot).filter(models.Slot.station_id == station_id).count()
    available_slots = db.query(models.Slot).filter(models.Slot.station_id == station_id, models.Slot.status == "available").count()

    # BOOKING STATS
    past_booking_count = db.query(models.Booking).filter(
        models.Booking.slot_id.in_(db.query(models.Slot.id).filter(models.Slot.station_id == station_id)),
        models.Booking.end_time < now
    ).count()

    upcoming_booking_count = db.query(models.Booking).filter(
        models.Booking.slot_id.in_(db.query(models.Slot.id).filter(models.Slot.station_id == station_id)),
        models.Booking.start_time >= now
    ).count()

    active_booking_count = db.query(models.Booking).filter(
        models.Booking.slot_id.in_(db.query(models.Slot.id).filter(models.Slot.station_id == station_id)),
        models.Booking.start_time <= now,
        models.Booking.end_time >= now
    ).count()

    # REVENUE FROM PAST BOOKINGS
    total_revenue = db.query(models.Booking).filter(
        models.Booking.slot_id.in_(db.query(models.Slot.id).filter(models.Slot.station_id == station_id)),
        models.Booking.end_time < now
    ).with_entities(func.sum(models.Booking.price)).scalar() or 0
    return {
        "station_id": station_id,
        "slots": {
            "total": total_slots,
            "available": available_slots
        },
        "bookings": {
            "past": past_booking_count,
            "upcoming": upcoming_booking_count,
            "active": active_booking_count
        },
        "revenue": float(total_revenue)
    }
