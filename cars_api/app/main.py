import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.routers.cars import cars_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registering routers
app.include_router(cars_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
