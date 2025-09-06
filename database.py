import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

# Create a MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Select the database (same as in connection string)
db = client["task_management_db"]
