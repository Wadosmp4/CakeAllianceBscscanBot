import logging

from typing import Callable, Dict, Any, Awaitable

from aiogram.fsm.middleware import BaseMiddleware
from aiogram.types import Message

from config import SUBSCRIBED_ADDRESSES


class CheckAccountAddress(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]):
        user_data = await data['state'].get_data()
        if user_data.get(SUBSCRIBED_ADDRESSES):
            return await handler(event, data)
        logging.error('User has not provided account address')
        await event.answer('To use this command please provide account address /subscribe_address')
