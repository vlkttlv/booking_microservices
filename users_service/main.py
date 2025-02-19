from fastapi import FastAPI
from users_service.router import router as users_router

app = FastAPI(title="Users microservice")
app.include_router(users_router)
