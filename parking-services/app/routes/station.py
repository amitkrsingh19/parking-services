from fastapi import APIRouter,Depends,status,HTTPException
from ..database import db
from ..auth_utils import get_current_user
from ..models import schemas
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorCollection

router=APIRouter(prefix="/stations",
                 tags=["stations"])

#post station 
@router.post("/", response_model=schemas.StationOut)
async def add_station(
    station: schemas.stationin,
    station_db: AsyncIOMotorCollection = Depends(db.get_station_collection),
    current_user: str = Depends(get_current_user)
):
    try:
        # Check for duplicate station ID
        station_exist = await station_db.find_one({"station_id": station.station_id})
        if station_exist:
            # Raise HTTP 409 Conflict with a message (not the full document)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Station with ID '{station.station_id}' already exists. Please proceed to adding slots.",
                headers={"message": "Conflict detected"}
            )
        #single admin - single station but multiple slots
        #check for admin
        admin_exist = await station_db.find_one({"posted_by":current_user})
        if admin_exist:
        # Raise HTTP 409 Conflict with a message (not the full document)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="admin cannot add multiple stations",
                headers={"message":"conflict detected"}
            ) 
        station_data = station.dict()
        station_data["station_id"] = station.station_id
        station_data["posted_by"] =current_user
        #insert station and return _id for the station
        result = await station_db.insert_one(station_data)

        return {
            "_id": str(result.inserted_id),
            **station_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)  # Convert error to string
        )
#delete station (only the admin created it & superadmin)
@router.delete("/")
async def del_station(station_db:AsyncIOMotorCollection=Depends(db.get_station_collection),
                      current_user:str=Depends(get_current_user)):
    try:
        #check for the station by admins id and delete
        await station_db.find_one_and_delete({"posted_by":current_user})
        #also confirm from the admin to delete later
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"message":"No posted station found"})
#Get station by ID
@router.get("/{id}")
async def get_station(
    id: str,
    station_db: AsyncIOMotorCollection = Depends(db.get_station_collection),
    current_user: str = Depends(get_current_user)
):
    try:
        found = await station_db.find_one({"station_id":id})
        if found:
            found["_id"] = str(found["_id"])  # ✅ Convert ObjectId to str
            return JSONResponse(status_code=status.HTTP_200_OK, content=found)
        else:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Station not found"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Invalid ID format"})

