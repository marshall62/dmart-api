# mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio

db_client: AsyncIOMotorClient = None
db = None

async def get_db_client() -> AsyncIOMotorClient:
    """Return database client instance."""
    return db_client


async def connect_db():
    global db, db_client
    """Create database connection."""
    CONNECTION_STRING=os.getenv("MONGO_DATASOURCE")
    print(f"Connection string:{CONNECTION_STRING}")
    db_client = AsyncIOMotorClient(CONNECTION_STRING)
    db = db_client.artworks


async def close_db():
    """Close database connection."""
    db_client.close()

async def test_query ():
    await connect_db()
    config = db.get_collection('config')
    conf = await config.find_one()
    print(f"Config is {conf}")
    return conf


def test_connect ():
    loop = asyncio.get_event_loop()
    coroutine = test_query()
    loop.run_until_complete(coroutine)
