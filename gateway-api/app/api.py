from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import Response, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from httpx import AsyncClient
from jose import jwt, JWTError
from app.config import settings


router = APIRouter()

# Service URLs (internal docker-compose network)
SERVICES = {
    "users": "http://user_services:8000",
    "parking": "http://parking_services:8000"
}

# Shared HTTP client
client = AsyncClient(timeout=30.0)

# OAuth2 token dependency (gateway handles auth at /login/)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8002/login"  # external gateway route
)

# ---------------------------
# Utility functions
# ---------------------------
async def forward_request(target_url: str, request: Request) -> Response:
    """Forward the incoming request to the target service."""
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    params = dict(request.query_params)
    content = await request.body()

    resp = await client.request(
        method=method,
        url=target_url,
        headers=headers,
        params=params,
        content=content,
    )

    content_type = resp.headers.get("content-type", "")
    safe_headers = {
        k: v for k, v in resp.headers.items()
        if k.lower() not in ("transfer-encoding", "content-encoding", "content-length", "connection")
    }

    if "application/json" in content_type:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
        return JSONResponse(status_code=resp.status_code, content=body, headers=safe_headers)

    return Response(content=resp.content, status_code=resp.status_code, headers=safe_headers, media_type=content_type)


async def get_current_user_payload(token: str = Depends(oauth2_scheme)):
    """Decode JWT and return user payload."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# ---------------------------
# Public Routes
# ---------------------------
@router.api_route("/user/users/", methods=["POST", "OPTIONS"])
async def proxy_create_user(request: Request):
    """Public: Create a new user (no auth required)."""
    try:
        return await forward_request(SERVICES["user"].rstrip("/") + "/users/", request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"user service unavailable: {e}")


@router.api_route("/login/", methods=["POST", "OPTIONS"])
async def proxy_login(request: Request):
    """Public: Forward login requests to user service."""
    try:
        return await forward_request(SERVICES["users"].rstrip("/") + "/login/", request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"user service unavailable: {e}")

# ---------------------------
# Protected Routes
# ---------------------------
@router.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "DELETE", "PATCH", "PUT", "OPTIONS"])
async def gateway_proxy(
    service_name: str,
    path: str,
    request: Request,
    user_payload: dict = Depends(get_current_user_payload),
):
    """Generic proxy for all services (requires valid token)."""

    if service_name not in SERVICES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")

    # Role-based access control
    if service_name == "parking" and user_payload.get("role") not in ["admin", "superadmin", "user"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for parking service")

    target_url = SERVICES[service_name].rstrip("/") + ("/" + path if path else "")

    try:
        return await forward_request(target_url, request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"{service_name} service unavailable: {e}")

# ---------------------------
# Debug Routes
# ---------------------------

@router.get("/test-user-service")
async def test_user_service():
    """Debug: Check connectivity to user service."""
    try:
        resp = await client.get(SERVICES["user"].rstrip("/") + "/")
        return {"status": "success", "user_service": "accessible", "response": resp.text}
    except Exception as e:
        return {"status": "error", "user_service": "unaccessible", "error": str(e)}
