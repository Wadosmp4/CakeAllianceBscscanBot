from typing import List, Dict, Any

from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.dispatcher.router import Router
from aiogram.fsm.state import StatesGroup, State

from bot.middlewares import CheckAccountAddress
from bot.utils import BscController, build_inline_keyboard
from config import bot, TRANSACTIONS_PER_PAGE, SUBSCRIBED_ADDRESSES, TRANSACTIONS, ID
from config.mongo import transactions_data

router = Router(name="bcs_commands")

router.message.middleware(CheckAccountAddress())


class PaginateTransactions(StatesGroup):
    waiting_for_account_address = State()
    waiting_for_pagination_action = State()


async def get_transactions_from_db_or_api(account_address: str, offset: slice, page: int) -> List[Dict[str, Any]]:
    if data := await transactions_data.find_one({ID: account_address}):
        result = list(data[TRANSACTIONS].values())[offset]
    else:
        data = await BscController.get_transactions_by_account(account_address, page=page, offset=TRANSACTIONS_PER_PAGE)
        result = BscController.transform_transaction_data(data)
    return result


@router.message(Command("history"))
async def cmd_bsc_history(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if not user_data[SUBSCRIBED_ADDRESSES]:
        await message.answer('You are not subscribed to any account addresses')
        return

    markup = build_inline_keyboard([(address, address) for address in user_data[SUBSCRIBED_ADDRESSES]])
    await state.set_state(PaginateTransactions.waiting_for_account_address)
    await message.answer('Select address you want to check history for',
                         reply_markup=markup)


@router.callback_query(PaginateTransactions.waiting_for_account_address)
async def cmd_first_page(callback_query: CallbackQuery, state: FSMContext):
    account_address = callback_query.data
    page = 1

    result = await get_transactions_from_db_or_api(account_address=account_address,
                                                   offset=slice(0, TRANSACTIONS_PER_PAGE),
                                                   page=page)

    markup = build_inline_keyboard([('Next', f'next_{page + 1}_{account_address}')])

    await state.set_state(PaginateTransactions.waiting_for_pagination_action)
    await bot.send_message(callback_query.from_user.id,
                           BscController.transactions_to_show(result),
                           reply_markup=markup,
                           parse_mode=ParseMode.HTML)


@router.callback_query(PaginateTransactions.waiting_for_pagination_action,
                       lambda c: c.data.startswith('next_') or c.data.startswith('prev_'))
async def history_pagination_handler(callback_query: CallbackQuery):
    _, page_str, account_address = callback_query.data.split('_')
    page = int(page_str)

    result = await get_transactions_from_db_or_api(account_address=account_address,
                                                   offset=slice(TRANSACTIONS_PER_PAGE * (page - 1),
                                                                TRANSACTIONS_PER_PAGE * page),
                                                   page=page)

    buttons = []
    if page != 1:
        buttons.append(("Previous", f'prev_{page - 1}_{account_address}'))
    if result and len(result) == TRANSACTIONS_PER_PAGE:
        buttons.append(("Next", f'next_{page + 1}_{account_address}'))

    markup = build_inline_keyboard(buttons)

    if not result:
        await bot.edit_message_text("This is the last page(",
                                    chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    reply_markup=markup)
        return

    await bot.edit_message_text(BscController.transactions_to_show(result),
                                chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                reply_markup=markup,
                                parse_mode=ParseMode.HTML)
