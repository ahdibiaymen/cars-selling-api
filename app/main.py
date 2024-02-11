from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from config import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On Startup

    # Initialize the connection with mongoDB database on application startup
    app.mongodb_client = AsyncIOMotorClient(Settings.DB_URL)
    app.mongodb = app.mongodb_client[Settings.DB_NAME]
    print('start')
    yield
    # On Shutdown

    # Close connection with mongodb database
    app.mongodb_client.close()


app = FastAPI(lifespan=lifespan)

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        reload=True
    )