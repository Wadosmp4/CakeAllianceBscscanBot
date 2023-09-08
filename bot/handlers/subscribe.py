from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.dispatcher.router import Router

from bot.utils import is_valid_bsc_address, build_inline_keyboard
from config.mongo import transactions_data
from config import bot, SUBSCRIBED_ADDRESSES, SUBSCRIBERS
from celery_app import load_transaction_data_task

router = Router(name="subscribe_commands")


class Subscribe(StatesGroup):
    waiting_for_account_address = State()
    waiting_for_load_data_confirm = State()


class Unsubscribe(StatesGroup):
    waiting_for_account_address = State()


@router.message(Command('subscribed_addresses'))
async def cmd_my_addresses(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if addresses := user_data[SUBSCRIBED_ADDRESSES]:
        await message.answer(f'You are subscribed to these addresses: {", ".join(addresses)}')
        return
    await message.answer('You are not subscribed to any account address')


@router.message(Command('subscribe_address'))
async def cmd_subscribe_address(message: Message, state: FSMContext):
    await state.set_state(Subscribe.waiting_for_account_address)
    await message.answer('Provide account address')


@router.message(Subscribe.waiting_for_account_address)
async def subscribe_to_address(message: Message, state: FSMContext):
    message_text = message.text
    if not is_valid_bsc_address(message_text):
        await message.answer("Provided account address is not valid, try again")
        return

    user_data = await state.get_data()
    if message_text in user_data[SUBSCRIBED_ADDRESSES]:
        await state.set_state(None)
        await message.answer("You already subscribed to this address")
        return
    await state.update_data({SUBSCRIBED_ADDRESSES: user_data[SUBSCRIBED_ADDRESSES] + [message_text]})

    address_data = await transactions_data.find_one({'_id': message_text})
    if not address_data:
        markup = build_inline_keyboard([('Yes', f'yes'), ('No', 'no')])
        await state.set_state(Subscribe.waiting_for_load_data_confirm)
        await message.answer('There are no saved data for this account address, '
                             'do you want to load data for this account address and get updates?\n'
                             'This will enable notifying when data about transactions added or updated',
                             reply_markup=markup)
        return

    await state.set_state(None)
    await transactions_data.update_one({'_id': message_text},
                                       {"$set": {SUBSCRIBERS: address_data[SUBSCRIBERS] + [message.chat.id]}})
    await message.answer("Subscription succeeded")


@router.callback_query(Subscribe.waiting_for_load_data_confirm, lambda c: c.data == 'yes')
async def load_data(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    load_transaction_data_task.delay(user_data[SUBSCRIBED_ADDRESSES][-1],
                                     callback_query.message.chat.id)
    await state.set_state(None)
    await bot.send_message(callback_query.from_user.id,
                           "Starting data loading, we will notify you when data is ready",
                           reply_markup=ReplyKeyboardRemove())


@router.callback_query(Subscribe.waiting_for_load_data_confirm, lambda c: c.data == 'no')
async def cancel_load(callback_query: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await state.update_data({SUBSCRIBED_ADDRESSES: user_data[SUBSCRIBED_ADDRESSES][:-1]})
    await state.set_state(None)
    await bot.send_message(callback_query.from_user.id,
                           "You did not approve use of data for receiving updates",
                           reply_markup=ReplyKeyboardRemove())


@router.message(Command('unsubscribe_address'))
async def cmd_unsubscribe_address(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if not user_data[SUBSCRIBED_ADDRESSES]:
        await message.answer('You have no subscriptions')
        return

    markup = build_inline_keyboard([(address, address) for address in user_data[SUBSCRIBED_ADDRESSES]])
    await state.set_state(Unsubscribe.waiting_for_account_address)
    await message.answer('Select address you want to unsubscribe',
                         reply_markup=markup)


@router.callback_query(Unsubscribe.waiting_for_account_address, lambda c: is_valid_bsc_address(c.data))
async def remove_subscription(callback_query: CallbackQuery, state: FSMContext):
    account_address = callback_query.data

    transactions = await transactions_data.find_one({'_id': account_address})
    transactions[SUBSCRIBERS].remove(callback_query.from_user.id)
    await transactions_data.update_one({'_id': account_address}, {"$set": {SUBSCRIBERS: transactions[SUBSCRIBERS]}})

    user_data = await state.get_data()
    user_data[SUBSCRIBED_ADDRESSES].remove(account_address)
    await state.update_data({SUBSCRIBED_ADDRESSES: user_data[SUBSCRIBED_ADDRESSES]})

    await state.set_state(None)
    await bot.send_message(callback_query.from_user.id,
                           f"Account address {account_address} is unsubscribed",
                           reply_markup=ReplyKeyboardRemove())
