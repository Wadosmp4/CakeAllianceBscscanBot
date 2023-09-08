from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Start bot'
        ),
        BotCommand(
            command='help',
            description='Help'
        ),
        BotCommand(
            command='cancel',
            description='Cancel action'
        ),
        BotCommand(
            command='subscribed_addresses',
            description='All subscribed addresses'
        ),
        BotCommand(
            command='subscribe_address',
            description='Subscribe to new address'
        ),
        BotCommand(
            command='unsubscribe_address',
            description='Unsubscribe from address'
        ),
        BotCommand(
            command='history',
            description='History of transactions'
        ),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
