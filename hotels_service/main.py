from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hotels_service.router import router as hotels_router
from hotels_service.router import api_router as api_hotels_router

app = FastAPI(title="Hotels microservice")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001", "http://localhost:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hotels_router)
app.include_router(api_hotels_router)
