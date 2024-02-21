from contextlib import asynccontextmanager

import uvicorn
from config import Settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app.routers.cars import cars_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On Startup

    # Initialize the connection with mongoDB database on application startup
    app.mongodb_client = AsyncIOMotorClient(Settings.DB_URL)
    app.mongodb = app.mongodb_client[Settings.DB_NAME]
    yield
    # On Shutdown

    # Close connection with mongodb database
    app.mongodb_client.close()


app = FastAPI(lifespan=lifespan)

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
