from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.dispatcher.router import Router

from config import SUBSCRIBED_ADDRESSES

router = Router(name="start_commands")


class Register(StatesGroup):
    waiting_for_account_address = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await state.update_data({SUBSCRIBED_ADDRESSES: [] if not user_data else user_data[SUBSCRIBED_ADDRESSES]})
    await message.answer("Welcome to My Telegram Bot!\n"
                         "Use /help to see available commands.")


@router.message(Command("cancel"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(None)
    await message.answer("Action cancelled")


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = ('Available commands:\n'
                 '/start - Start interaction with bot\n'
                 '/cancel - Cancel action\n'
                 '/subscribed_addresses - All subscribed addresses\n'
                 '/subscribe_address - Subscribe to new address\n'
                 '/unsubscribe_address - Unsubscribe from address\n'
                 '/history - History of transactions\n'
                 '/help - Show this help message\n')
    await message.answer(help_text)
