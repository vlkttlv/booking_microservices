from fastapi import FastAPI
from booking_service.router import router as booking_router
from booking_service.router import api_router as api_booking_router

app = FastAPI(title="Booking Microservice")
app.include_router(booking_router)
app.include_router(api_booking_router)