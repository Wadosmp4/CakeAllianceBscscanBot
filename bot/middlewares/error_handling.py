import logging

from typing import Callable, Dict, Any, Awaitable

from aiogram.fsm.middleware import BaseMiddleware
from aiogram.types import Message


class ErrorHandlingMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]):
        try:
            return await handler(event, data)
        except Exception as exc:
            logging.error(f"Error in message processing: {exc}")
            error_message = "An error occurred while processing your request. Please try again later."
            await event.answer(error_message)
