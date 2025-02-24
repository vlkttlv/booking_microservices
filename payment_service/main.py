from fastapi import FastAPI
from payment_service.router import router as payment_router
from payment_service.router import api_router as api_payment_router

app = FastAPI(title="Payment Microservice")
app.include_router(payment_router)
app.include_router(api_payment_router)