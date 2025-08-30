from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from jose import jwt, JWTError
from app import api,auth
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title="Parking System Gateway API", version="1.0.0")

# CORS Configuration - Allow frontend to connect
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative frontend port
    "http://localhost:8000",  # Gateway API
    "http://localhost:8001",
    "http://localhost:8002"
    "http://127.0.0.1:5173", # Alternative localhost
    "http://127.0.0.1:3000", # Alternative localhost
    "http://127.0.0.1:8000", # Alternative localhost
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8002"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api.router)
app.include_router(auth.router)

# Middleware: verify JWT once
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Missing token"})

    token = token.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        request.state.user = payload
    except JWTError:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    return await call_next(request)

@app.get("/")
async def root():
    return {
        "message": "Parking System Gateway API",
        "version": "1.0.0",
        "status": "running",
        "services": ["user", "parking"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway"}



