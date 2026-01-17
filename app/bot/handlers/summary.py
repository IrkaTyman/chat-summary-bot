from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards.choose_n import choose_n_kb, ChooseNCallback
from app.bot.utils.text import split_text
from app.services.telegram_reader import TelegramReader, normalize_channel_identifier
from app.services.summarizer import SummarizerStub
from app.services.telethon_errors import humanize_telethon_error
import logging
from app.db.di import SessionFactory
from app.db.repositories.subscriptions import SubscriptionRepo
from app.bot.keyboards.pick_channel import pick_channel_kb, PickChannelCallback
from app.bot.keyboards.choose_n_sub import choose_n_sub_kb, ChooseNSubCallback

logger = logging.getLogger(__name__)

router = Router()

MAX_N = 100


def _parse_args(text: str) -> tuple[str | None, int | None, bool]:
    """
    returns: (channel, n, n_was_provided)
    """
    parts = (text or "").split()
    if len(parts) < 2:
        return None, None, False

    channel = parts[1]
    if len(parts) < 3:
        return channel, None, False

    try:
        return channel, int(parts[2]), True
    except ValueError:
        return channel, None, True


async def _run_mode(message: Message, mode: str, channel: str, n: int, tg_reader: TelegramReader) -> None:
    if n < 1 or n > MAX_N:
        await message.answer(f"n должно быть от 1 до {MAX_N}.")
        return

    try:
        posts = await tg_reader.get_last_posts(channel, n)
    except Exception as e:
        logger.exception("Telethon error while reading channel=%s", channel)
        await message.answer(humanize_telethon_error(e))
        return

    s = SummarizerStub()
    if mode == "themes":
        result = s.themes(posts)
    else:
        result = s.summarize(posts)

    text = f"{result.title} для {channel} (последние {n} постов)\n\n{result.body}"
    for part in split_text(text):
        await message.answer(part)


@router.message(Command("summary"))
async def cmd_summary(message: Message, tg_reader: TelegramReader, db_session_factory: SessionFactory) -> None:
    channel, n, n_was_provided = _parse_args(message.text)

    
    if not channel:
        # показать список сохранённых каналов
        async with db_session_factory() as session:
            subs = await SubscriptionRepo.list_subscriptions(session, message.from_user.id)

        if not subs:
            await message.answer("У вас нет сохранённых каналов. Добавьте: /subscribe @channel")
            return

        await message.answer("Выберите канал для саммари:", reply_markup=pick_channel_kb("summary", subs))
        return

    if not n:
        if n_was_provided:
            await message.answer("n должно быть числом. Выберите вариант кнопкой:")
        normalized = normalize_channel_identifier(channel)
        await message.answer(
            f"Выберите количество последних постов для {channel}:",
            reply_markup=choose_n_kb("summary", normalized),
        )
        return

    normalized = normalize_channel_identifier(channel)
    await _run_mode(message, "summary", normalized, n, tg_reader)


@router.message(Command("themes"))
async def cmd_themes(message: Message, tg_reader: TelegramReader, db_session_factory: SessionFactory) -> None:
    channel, n, n_was_provided = _parse_args(message.text)

    if not channel:
        async with db_session_factory() as session:
            subs = await SubscriptionRepo.list_subscriptions(session, message.from_user.id)

        if not subs:
            await message.answer("У вас нет сохранённых каналов. Добавьте: /subscribe @channel")
            return

        await message.answer("Выберите канал для тем:", reply_markup=pick_channel_kb("themes", subs))
        return

    if not n:
        if n_was_provided:
            await message.answer("n должно быть числом. Выберите вариант кнопкой:")
        normalized = normalize_channel_identifier(channel)
        await message.answer(
            f"Выберите количество последних постов для {channel}:",
            reply_markup=choose_n_kb("summary", normalized),
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

@router.callback_query(PickChannelCallback.filter())
async def on_pick_channel_callback(
    call: CallbackQuery,
    callback_data: PickChannelCallback,
    db_session_factory: SessionFactory,
) -> None:
    if callback_data.mode == "cancel":
        await call.answer("Отменено")
        return

    user_id = call.from_user.id
    async with db_session_factory() as session:
        sub = await SubscriptionRepo.get_subscription_by_id(session, user_id, callback_data.sub_id)

    if not sub:
        await call.answer("Подписка не найдена", show_alert=True)
        return

    ident = sub.channel_identifier
    if not ident.startswith("@"):
        ident_show = "@" + ident
    else:
        ident_show = ident

    await call.message.answer(
        f"Выберите количество последних постов для {ident_show}:",
        reply_markup=choose_n_sub_kb(callback_data.mode, sub.id),
    )
    await call.answer()

@router.callback_query(ChooseNSubCallback.filter())
async def on_choose_n_sub_callback(
    call: CallbackQuery,
    callback_data: ChooseNSubCallback,
    tg_reader: TelegramReader,
    db_session_factory: SessionFactory,
) -> None:
    user_id = call.from_user.id
    async with db_session_factory() as session:
        sub = await SubscriptionRepo.get_subscription_by_id(session, user_id, callback_data.sub_id)

    if not sub:
        await call.answer("Подписка не найдена", show_alert=True)
        return

    # sub.channel_identifier хранится нормализованным (обычно без @)
    channel = sub.channel_identifier

    await _run_mode(call.message, callback_data.mode, channel, callback_data.n, tg_reader)
    await call.answer()
