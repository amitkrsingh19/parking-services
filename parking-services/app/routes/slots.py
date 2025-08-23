from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import schemas, models
from app.database import db 
from app.dependencies import auth_utils
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/slots",
    tags=["slots"]
)

# ------------------------
# CREATE SLOT (ADMIN ONLY)
# ------------------------
@router.post("/",response_model=schemas.SlotOut)
def create_slot(
    slot: schemas.SlotCreate,
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    admin_id = payload.get("sub")

    # check that station exists
    station = db.query(models.Parking).filter(models.Parking.id == slot.station_id).first()
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station id not found. Cannot add slots.",
            headers={"message": "Please enter a valid station_id to add slot."}
        )
     # Create new slot object
    new_slot = models.Slot(
        station_id=slot.station_id,
        slot_number=slot.slot_number,
        slot_type=slot.slot_type,
        status=slot.status,
        admin_id=admin_id)
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    return new_slot


# ------------------------
# GET AVAILABLE SLOTS (USER)
# ------------------------
@router.get("/",response_model=schemas.SlotShow, dependencies=[Depends(auth_utils.requires_role("user"))])
def fetch_slot(
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload),
    skip: int = 0,
    limit: int = 10
):
    slots = db.query(models.Slot).filter(models.Slot.status == True).offset(skip).limit(limit).all()
    return slots


# ------------------------
# GET SLOT BY ID (USER)
# ------------------------
@router.get("/{id}", dependencies=[Depends(auth_utils.requires_role("user"))], response_model=schemas.SlotOut)
def get_slot(
    id: int,
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    slot = db.query(models.Slot).filter(models.Slot.id == id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return slot


# ------------------------
# GET ALL SLOTS POSTED BY ADMIN (SUPERADMIN)
# ------------------------
@router.get("/-admin", dependencies=[Depends(auth_utils.requires_role("superadmin"))])
def get_slots(
    db: Session = Depends(db.get_db),
    payload: dict = Depends(auth_utils.get_token_payload)
):
    user_id = payload.get("sub")

    slots = db.query(models.Slot).filter(models.Slot.admin_id == user_id).all()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"slots": [s.__dict__ for s in slots]})
