from fastapi import APIRouter,Depends,HTTPException,status
from ..models import schemas
from ..database import db
from app.dependencies import auth_utils
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorCollection

router=APIRouter(prefix="/slots",
                 tags=["slots"])

# create a slot by admin 
# to create a slot admin must have a station
@router.post("/")
async def create_slot(
    slot: schemas.SlotCreate,
    slot_db: AsyncIOMotorCollection = Depends(db.get_parking_collection),
    station_db: AsyncIOMotorCollection = Depends(db.get_station_collection),
    payload:dict=Depends(auth_utils.get_token_payload)
):
    try:
        #get user id from payload
        user_id=payload.get("sub")
        #check that station id exist
        station_found=station_db.find_one({"station_id":slot.station_id})
        if not station_found:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="station id not found ,Cant add slots",
                                     headers={"message":"please enter a valid  station_id to add slot."})
        # Convert Pydantic model to dict
        slot_data = slot.dict()
        #add admin user_id in slot db
        slot_data["admin"]=user_id
        # Insert the new slot
        result = await  slot_db.insert_one(slot_data)
        # Prepare response
        slot_data["_id"] = str(result.inserted_id)
        slot_data["station_id"] = str(slot_data["station_id"])
        return slot_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#get slot for users
@router.get("/")
async def fetch_slot(skip:int=0,limit:int=0,slot_db: AsyncIOMotorCollection = Depends(db.get_parking_collection),
               payload:str=Depends(auth_utils.get_token_payload)):
    slots_cursor= slot_db.find({"is_available":"True"})
    available_slot=[]
    async for doc in slots_cursor:
        available_slot.append(doc)
    return available_slot
     
# Get  Slot By ID for users
@router.get("/{id}", response_model=schemas.SlotOut)
async def get_slot(id:str, slot_db: AsyncIOMotorCollection = Depends(db.get_parking_collection),
                   payload:str=Depends(auth_utils.get_token_payload)):
    result = await slot_db.find_one({"slot_id":id})
    if not result:
        raise HTTPException(status_code=404, detail="Slot not found")

    slot_response = {
        "slot_id": str(result["_id"]),
        "station_id": str(result["station_id"]),
        "is_available": result["is_available"],
        "charging_support": result["charging_support"]
    }

    return schemas.SlotOut(**slot_response)

#get all the posted slots for admin
@router.get("/-admin")
async def get_slots(slot_db:AsyncIOMotorCollection=Depends(db.get_parking_collection),
                    payload:dict=Depends(auth_utils.get_token_payload)):
    #get user_id from payload
    user_id=payload.get("sub")
    slots_cursor=slot_db.find({"admin":user_id})
    slots=[]
    async for documents in slots_cursor:
        documents["_id"]=str(documents["_id"])
        slots.append(documents)
    return JSONResponse(status_code=status.HTTP_200_OK,content={"slots":slots})

