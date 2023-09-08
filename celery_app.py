import asyncio
import logging

from aiogram.enums import ParseMode
from celery import Celery

from config import bot, RABBITMQ_URL, REDIS_URL, TRANSACTION_FORMAT, TRANSACTIONS, SUBSCRIBERS, ID
from config.mongo import transactions_data
from bot.utils import BscController
from asgiref.sync import async_to_sync


celery_app = Celery(broker=RABBITMQ_URL,
                    backend=REDIS_URL)

celery_app.autodiscover_tasks(force=True)


async def create_check_updates_tasks():
    cursor = transactions_data.find({})
    while await cursor.fetch_next:
        transaction = cursor.next_object()
        update_data_task.delay(transaction[ID])


async def load_transaction_data(account_address, chat_id):
    result = await BscController.get_all_transactions(account_address)
    result = BscController.transform_transaction_data(result)

    await transactions_data.insert_one({ID: account_address,
                                        TRANSACTIONS: {value[ID]: value for value in result},
                                        SUBSCRIBERS: [chat_id]})
    await bot.send_message(chat_id, 'Data loaded successfully for {}'.format(account_address))

    update_data_task.delay(account_address)


@celery_app.task(serializer='json')
def load_transaction_data_task(account_address, chat_id):
    async_to_sync(load_transaction_data)(account_address, chat_id)


async def update_data(account_address):
    while True:
        result = await BscController.get_all_transactions(account_address)
        result = BscController.transform_transaction_data(result)

        address_data = await transactions_data.find_one({ID: account_address})
        address_transactions = address_data[TRANSACTIONS]
        subscribers = address_data[SUBSCRIBERS]

        new_transactions = False
        for value in result:
            if value not in address_transactions.values():
                new_transactions = True
                address_transactions[value[ID]] = value
                for subscriber in subscribers:
                    await bot.send_message(subscriber,
                                           "New transaction \n" + TRANSACTION_FORMAT.format(**value),
                                           parse_mode=ParseMode.HTML)

        if new_transactions:
            logging.info("Data changed for {}".format(account_address))
            await transactions_data.update_one({ID: account_address},
                                               {'$set': {TRANSACTIONS: address_transactions}})
        else:
            logging.info("No data changes for {}".format(account_address))
        await asyncio.sleep(60.0)


@celery_app.task(serializer='json')
def update_data_task(account_address):
    async_to_sync(update_data)(account_address)
