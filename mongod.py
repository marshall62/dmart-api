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
    print(f"Connecting to db with {CONNECTION_STRING}")
    db_client = AsyncIOMotorClient(CONNECTION_STRING)
    print(f"The db_client is {db_client}")
    db = db_client.artworks
    print(f"The database is {db}")

async def close_db():
    """Close database connection."""
    print(f"Closing db_client")
    db_client.close()