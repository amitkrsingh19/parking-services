from fastapi import FastAPI
from app import api
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

Origins = [
    "http://localhost:8000",  # for your local frontend development
    "http://0.0.0.0:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=Origins,  # Specifies the allowed origins
    allow_credentials=True, # Allows cookies and authorization headers
    allow_methods=["*"],    # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],    # Allows all headers
)
app.include_router(api.router)



