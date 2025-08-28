from fastapi import FastAPI
from app import api
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Parking System Gateway API", version="1.0.0")

# CORS Configuration - Allow frontend to connect
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative frontend port
    "http://localhost:8000",  # Gateway API
    "http://127.0.0.1:5173", # Alternative localhost
    "http://127.0.0.1:3000", # Alternative localhost
    "http://127.0.0.1:8000", # Alternative localhost
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



