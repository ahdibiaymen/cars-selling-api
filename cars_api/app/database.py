from app.config import Settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


# MongoDB database dependency
async def mongodb_client() -> AsyncIOMotorDatabase:
    database = AsyncIOMotorClient(Settings.DB_URL)
    client = database[Settings.DB_NAME]
    yield client
