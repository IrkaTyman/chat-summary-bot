from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.db.models import Subscription


class PickChannelCallback(CallbackData, prefix="pick_ch"):
    mode: str   # "summary" | "themes"
    sub_id: int


def pick_channel_kb(mode: str, subs: list[Subscription]) -> InlineKeyboardMarkup:
    rows = []
    for s in subs:
        ident = s.channel_identifier
        if not ident.startswith("@"):
            ident = "@" + ident
        rows.append(
            [InlineKeyboardButton(text=ident, callback_data=PickChannelCallback(mode=mode, sub_id=s.id).pack())]
        )

    rows.append([InlineKeyboardButton(text="Отмена", callback_data=PickChannelCallback(mode="cancel", sub_id=0).pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)
