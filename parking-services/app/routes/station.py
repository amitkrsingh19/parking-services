from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.database import db
from app.dependencies import auth_utils
from app.models import schemas, models

router = APIRouter(
    prefix="/stations",
    tags=["stations"]
)

# ----------------------------
# POST Station (Admin only)
# ----------------------------
@router.post(
    "/",
    dependencies=[Depends(auth_utils.requires_role("admin"))],
    response_model=schemas.StationOut
)
def add_station(
    station: schemas.StationIn,
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    try:
        user_id = payload.get("sub")

        # Check if station already exists by name/location combo
        station_exist = (
            db.query(models.Parking)
            .filter(models.Parking.name == station.station_name,
                    models.Parking.location == station.location)
            .first()
        )
        if station_exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Station '{station.station_name}' at '{station.location}' already exists. Please proceed to adding slots.",
                headers={"message": "Conflict detected"}
            )

        # One admin → one station (enforced)
        admin_exist = (
            db.query(models.Parking)
            .filter(models.Parking.owner_id == user_id)
            .first()
        )
        if admin_exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Admin cannot add multiple stations",
                headers={"message": "Conflict detected"}
            )

        # Create new station
        new_station = models.Parking(
            name=station.station_name,
            location=station.location,
            capacity=station.capacity,
            owner_id=user_id,
        )
        db.add(new_station)
        db.commit()
        db.refresh(new_station)

        return new_station

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ----------------------------
# DELETE Station (Superadmin or Admin who owns it)
# ----------------------------
@router.delete(
    "/{station_id}",
    dependencies=[Depends(auth_utils.requires_role("superadmin"))]
)
def del_station(
    station_id: int,
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    try:
        user_id = payload.get("sub")

        station = db.query(models.Parking).filter(
            models.Parking.id == station_id
        ).first()

        if not station:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Station not found"
            )

        # If user is admin → must be owner; superadmin bypasses
        role = payload.get("role")
        if role == "admin" and station.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only delete their own stations"
            )

        db.delete(station)
        db.commit()
        return {"message": f"Station {station_id} deleted successfully"}

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "No posted station found"}
        )

# ----------------------------
# GET Station by ID (Any role)
# ----------------------------
@router.get(
    "/{station_id}",
    dependencies=[Depends(auth_utils.requires_role("user"))]
)
def get_station(
    station_id: int,
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    try:
        found = db.query(models.Parking).filter(
            models.Parking.id == station_id
        ).first()

        if not found:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Station not found"}
            )

        return found

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Invalid ID format"}
        )
