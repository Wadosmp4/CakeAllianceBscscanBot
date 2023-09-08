from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from .config import TELEGRAM_BOT_TOKEN, REDIS_URL, BSC_SCAN_API_KEY, RABBITMQ_URL, MONGO_URL, ADMIN_USER_ID
from .bot_comands import set_commands
from .constants import (WEI_TO_BNB, TRANSACTION_FORMAT, TRANSACTIONS_PER_PAGE, DATE_FORMAT, SUBSCRIBED_ADDRESSES,
                        SUBSCRIBERS, TRANSACTIONS, ID)


storage = RedisStorage.from_url(REDIS_URL)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=storage)
