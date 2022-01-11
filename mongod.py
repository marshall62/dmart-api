# mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

db_client: AsyncIOMotorClient = None
db = None

async def get_db_client() -> AsyncIOMotorClient:
    """Return database client instance."""
    return db_client


async def connect_db():
    global db, db_client
    """Create database connection."""
    CONNECTION_STRING=os.getenv("MONGO_DATASOURCE")
    db_client = AsyncIOMotorClient(CONNECTION_STRING)
    db = db_client.artworks


async def close_db():
    """Close database connection."""
    db_client.close()