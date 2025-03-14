from fastapi import FastAPI
from payment_service.router import router as payment_router
from payment_service.router import api_router as api_payment_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Payment Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001", "http://localhost:8002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payment_router)
app.include_router(api_payment_router)