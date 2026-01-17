from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class ChooseNSubCallback(CallbackData, prefix="choose_n_sub"):
    mode: str    # "summary" | "themes"
    sub_id: int
    n: int


def choose_n_sub_kb(mode: str, sub_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="10", callback_data=ChooseNSubCallback(mode=mode, sub_id=sub_id, n=10).pack())],
            [InlineKeyboardButton(text="20", callback_data=ChooseNSubCallback(mode=mode, sub_id=sub_id, n=20).pack())],
            [InlineKeyboardButton(text="50", callback_data=ChooseNSubCallback(mode=mode, sub_id=sub_id, n=50).pack())],
        ]
    )
