from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.choose_n import summary_choose_n_kb, SummaryNCallback
from app.services.telegram_reader import TelegramReader

router = Router()


def _parse_summary_args(text: str) -> tuple[str | None, int | None]:
    parts = (text or "").split()
    if len(parts) < 2:
        return None, None
    channel = parts[1]
    n = None
    if len(parts) >= 3:
        try:
            n = int(parts[2])
        except ValueError:
            n = None
    return channel, n


@router.message(Command("summary"))
async def cmd_summary(message: Message, tg_reader: TelegramReader) -> None:
    channel, n = _parse_summary_args(message.text)

    if not channel:
        await message.answer("Формат: /summary <channelNick/channelUrl> <n>\nПример: /summary @durov 10")
        return

    if not n:
        await message.answer(
            f"Выберите количество последних постов для {channel}:",
            reply_markup=summary_choose_n_kb(channel),
        )
        return

    if n < 1 or n > 100:
        await message.answer("n должно быть от 1 до 100.")
        return

    posts = await tg_reader.get_last_posts(channel, n)

    lines = [f"Получено постов: {len(posts)} (последние {n})\n"]
    for i, p in enumerate(posts[:5], start=1):
        t = p.text.replace("\n", " ")
        if len(t) > 160:
            t = t[:160] + "…"
        lines.append(f"{i}) {t}")

    await message.answer("\n".join(lines))


@router.callback_query(SummaryNCallback.filter())
async def on_summary_n_callback(call: CallbackQuery, callback_data: SummaryNCallback, tg_reader: TelegramReader) -> None:
    posts = await tg_reader.get_last_posts(callback_data.channel, callback_data.n)

    lines = [f"Получено постов: {len(posts)} (последние {callback_data.n})\n"]
    for i, p in enumerate(posts[:5], start=1):
        t = p.text.replace("\n", " ")
        if len(t) > 160:
            t = t[:160] + "…"
        lines.append(f"{i}) {t}")

    await call.message.answer("\n".join(lines))
    await call.answer()
