from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import httpx

router = APIRouter(prefix="/auth", tags=["auth"])

USER_SERVICE_URL = "http://user-services:8000"  # internal Docker service name

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Proxy login: forwards username/password to user-service and returns token.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{USER_SERVICE_URL}/login/",
                data={"username": form_data.username, "password": form_data.password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"User service unreachable: {e}")

    # now check status after request is guaranteed to have completed
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()
