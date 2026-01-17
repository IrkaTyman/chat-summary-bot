from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class ChooseNCallback(CallbackData, prefix="choose_n"):
    mode: str   # "summary" | "themes"
    channel: str
    n: int


def choose_n_kb(mode: str, channel: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="10", callback_data=ChooseNCallback(mode=mode, channel=channel, n=10).pack())],
            [InlineKeyboardButton(text="20", callback_data=ChooseNCallback(mode=mode, channel=channel, n=20).pack())],
            [InlineKeyboardButton(text="50", callback_data=ChooseNCallback(mode=mode, channel=channel, n=50).pack())],
        ]
    )
