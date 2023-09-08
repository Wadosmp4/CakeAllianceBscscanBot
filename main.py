import asyncio
import logging

from asyncio import sleep

from config import bot, dp, ADMIN_USER_ID, set_commands
from bot.handlers import start_router, register_router, transaction_router
from bot.middlewares import ErrorHandlingMiddleware

from celery_app import create_check_updates_tasks

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')


async def start_bot():
    await sleep(10)
    await set_commands(bot)
    await create_check_updates_tasks()
    await bot.send_message(ADMIN_USER_ID, text='Bot started!')


async def stop_bot():
    await bot.send_message(ADMIN_USER_ID, text='Bot stopped!')


async def start():
    # routers
    dp.include_router(start_router)
    dp.include_router(register_router)
    dp.include_router(transaction_router)

    # general middlewares
    dp.message.middleware(ErrorHandlingMiddleware())

    # actions start and stop
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
