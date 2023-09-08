from config import MONGO_URL
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(MONGO_URL)
db = client['db']

transactions_data = db['transactions_data']
