from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.choose_n import choose_n_kb, ChooseNCallback
from app.bot.utils.text import split_text
from app.services.telegram_reader import TelegramReader, normalize_channel_identifier
from app.services.summarizer import SummarizerStub

router = Router()

MAX_N = 100


def _parse_args(text: str) -> tuple[str | None, int | None]:
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


async def _run_mode(message: Message, mode: str, channel: str, n: int, tg_reader: TelegramReader) -> None:
    if n < 1 or n > MAX_N:
        await message.answer(f"n должно быть от 1 до {MAX_N}.")
        return

    posts = await tg_reader.get_last_posts(channel, n)

    s = SummarizerStub()
    if mode == "themes":
        result = s.themes(posts)
    else:
        result = s.summarize(posts)

    text = f"{result.title} для {channel} (последние {n} постов)\n\n{result.body}"
    for part in split_text(text):
        await message.answer(part)


@router.message(Command("summary"))
async def cmd_summary(message: Message, tg_reader: TelegramReader) -> None:
    channel, n = _parse_args(message.text)

    if not channel:
        await message.answer("Формат: /summary <channelNick/channelUrl> <n>\nПример: /summary @durov 10")
        return

    if not n:
        normalized = normalize_channel_identifier(channel)
        await message.answer(
            f"Выберите количество последних постов для {channel}:",
            reply_markup=choose_n_kb("summary", normalized),
        )
        return

    normalized = normalize_channel_identifier(channel)
    await _run_mode(message, "summary", normalized, n, tg_reader)


@router.message(Command("themes"))
async def cmd_themes(message: Message, tg_reader: TelegramReader) -> None:
    channel, n = _parse_args(message.text)

    if not channel:
        await message.answer("Формат: /themes <channelNick/channelUrl> <n>\nПример: /themes @durov 10")
        return

    if not n:
        normalized = normalize_channel_identifier(channel)
        await message.answer(
            f"Выберите количество последних постов для {channel}:",
            reply_markup=choose_n_kb("themes", normalized),
        )
        return

    normalized = normalize_channel_identifier(channel)
    await _run_mode(message, "themes", normalized, n, tg_reader)


@router.callback_query(ChooseNCallback.filter())
async def on_choose_n_callback(
    call: CallbackQuery,
    callback_data: ChooseNCallback,
    tg_reader: TelegramReader,
) -> None:
    # call.message is Message
    await _run_mode(call.message, callback_data.mode, callback_data.channel, callback_data.n, tg_reader)
    await call.answer()
