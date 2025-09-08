import motor.motor_asyncio
import os
import asyncio
from dotenv import load_dotenv

# Load .env
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

async def test_connection():
    # list_database_names is async, so we await it
    dbs = await client.list_database_names()
    print("Databases:", dbs)

asyncio.run(test_connection())
