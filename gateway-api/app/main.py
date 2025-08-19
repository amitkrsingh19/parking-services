from fastapi import FastAPI
from app import api
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

Origins=["http://localhost:8000",
         "http://0.0.0.0:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,

)
app.include_router(api.router)



