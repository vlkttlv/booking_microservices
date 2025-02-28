from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from booking_service.router import router as booking_router
from booking_service.router import api_router as api_booking_router

app = FastAPI(title="Booking Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001", "http://localhost:8003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(booking_router)
app.include_router(api_booking_router)

