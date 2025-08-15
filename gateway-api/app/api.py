from fastapi import FastAPI,APIRouter,Depends,Body
from app.dependencies import requires_role
from typing import Dict
import requests
#station endpoint
router=APIRouter()

#add station endpoint
@router.post("/stations",dependencies=[Depends(requires_role("superadmin"))])
def create_station_endpoint(station_data:Dict=Body()):
    response=requests.post("https://parking-services:8002/stations/",json=station_data)
    
    response.raise_for_status()

    return response.json()

#get all the users endpoint
@router.get("/users",dependencies=[Depends(requires_role("superadmin"))])
def get_users():
    response=requests.get("https://user-services:8001/users/")

    # Check for HTTP errors
    response.raise_for_status()

    return response.json()

#register admin endpoint 
@router.post("/users/register-admin", dependencies=[Depends(requires_role("superadmin"))])
def create_admin(user_data:Dict=Body()):
    response=requests.post("https://user-services:8001/users/register-admin/",json=user_data)

    response.raise_for_status()

    return response.json()

#add slots endpoint
@router.post("/slots",dependencies=[Depends(requires_role("superadmin"or"admin"))])
def create_slots_endpoint(slot_data:Dict=Body()):
    
    response=requests.post("https://parking-services:8002/slots/",json=slot_data)
    
    # Check for HTTP errors
    response.raise_for_status()

    return response.json()


# delete slots endpoint 
@router.delete("/slots/{slot_id}", dependencies=[Depends(requires_role("admin"))])
def delete_slots_endpoint(slot_id: str):
    response = requests.delete(f"https://parking-services:8002/slots/{slot_id}")
    
    # Check for HTTP errors
    response.raise_for_status()
    
    # Return the response from the downstream service
    return response.json()

#create slot end point
@router.post("/slots",dependencies=[Depends(requires_role("admin"))])
def create_slot_endpoint():
    pass

#delete slots endpoint
@router.delete("/slots",dependencies=[Depends(requires_role("admin"))])
def del_slot_endpoint():
    pass

@router.get("/slots",dependencies=[Depends(requires_role("user"))])
def get_slots_endpoint():
    pass

@router.post("users/register")
def register_user_endpoint():
    pass