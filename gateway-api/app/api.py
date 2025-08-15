from fastapi import FastAPI,APIRouter,Depends,Body,requests,Request,status,HTTPException,Depends
from app.dependencies import requires_role
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient
from config import SECRET_KEY,ALGORITHM
from jose import jwt,JWTError
from httpx import AsyncClient


#station endpoint
router=APIRouter()
# services
services={
    "user":"http://user-services:8001",
    "parking":"http://parking-services:8002",
    "booking":"http://booking-services:8003"
}
client = AsyncClient(base_url="http://localhost")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# This dependency is used to extract the token from the header
async def get_current_user_payload(token: str = Depends(oauth2_scheme)):
    # The gateway's logic to decode and validate the token
    # This is a critical step to prevent forwarding unauthenticated requests
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") 
    
@router.api_route("/{service_name}/{path:path}",methods=["GET","POST","DELETE","PATCH"] )
async def gateway_proxy(service_name:str,
                        path:str,
                        request:Request,
                        user_payload:dict=Depends(get_current_user_payload)):
    # Check if the requested service exists in our mapping
    if service_name not in services:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message":"Service not Found"})
    # only admin can acces parking services
    if service_name == "parking":
        requires_role("admin")
    # Construct the correct internal URL for the microservice
    internal_url = f"{services[service_name]}/{path}"
    #get method
    method=request.method
    #get headers
    headers=dict(request.headers)
    #remove host from header
    headers.pop("host",None)
    #get body
    body=await request.body()
    try:
    #Await the request to Microservices
    #genrate response
        response = await client.request(method=method,
                                        url=internal_url,
                                        headers=headers,
                                        content=body)
        
        response.raise_for_status()
        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
            headers=dict(response.headers))
    except Exception as e:
        # Handle cases where the microservice is down or unreachable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"The {service_name} service is currently unavailable. Error: {e}")

