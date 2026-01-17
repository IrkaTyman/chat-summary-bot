from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class SummaryNCallback(CallbackData, prefix="sum"):
    channel: str
    n: int


def summary_choose_n_kb(channel: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="10", callback_data=SummaryNCallback(channel=channel, n=10).pack())],
            [InlineKeyboardButton(text="20", callback_data=SummaryNCallback(channel=channel, n=20).pack())],
            [InlineKeyboardButton(text="50", callback_data=SummaryNCallback(channel=channel, n=50).pack())],
        ]
    )
