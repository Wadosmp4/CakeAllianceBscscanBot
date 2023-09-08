import re

from typing import List, Tuple

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def is_valid_bsc_address(address: str) -> bool:
    # BSC addresses should be 40 characters long and hexadecimal
    if re.match(r'^0x[0-9a-fA-F]{40}$', address):
        return True
    return False


def build_inline_keyboard(buttons: List[Tuple[str, str]]) -> InlineKeyboardMarkup:
    processed_buttons = []
    for button_text, callback_data in buttons:
        button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
        processed_buttons.append(button)
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[processed_buttons])
    return inline_keyboard
