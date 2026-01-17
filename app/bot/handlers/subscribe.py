from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.db.di import SessionFactory
from app.db.repositories.subscriptions import SubscriptionRepo
from app.services.telegram_reader import TelegramReader, normalize_channel_identifier

router = Router()

MAX_SUBSCRIPTIONS = 10


def _parse_channel(text: str) -> str | None:
    parts = (text or "").split()
    if len(parts) < 2:
        return None
    return parts[1]


@router.message(Command("subscribe"))
async def cmd_subscribe(message: Message, tg_reader: TelegramReader, db_session_factory: SessionFactory) -> None:
    raw_channel = _parse_channel(message.text)
    if not raw_channel:
        await message.answer("Формат: /subscribe <channelNick/channelUrl>\nПример: /subscribe @durov")
        return

    channel = normalize_channel_identifier(raw_channel)

    # 1) резолвим канал через Telethon (валидируем что существует/доступен)
    try:
        channel_id = await tg_reader.resolve_channel_id(channel)
    except Exception:
        await message.answer("Не получилось получить доступ к каналу. Проверьте ссылку/ник и что аккаунт Telethon видит канал.")
        return

    user_id = message.from_user.id

    async with db_session_factory() as session:
        async with session.begin():
            await SubscriptionRepo.ensure_user(session, user_id)

            count = await SubscriptionRepo.count_user_subscriptions(session, user_id)
            if count >= MAX_SUBSCRIPTIONS:
                await message.answer(f"Лимит подписок: {MAX_SUBSCRIPTIONS}. Сначала отпишитесь от одного канала.")
                return

            created, msg = await SubscriptionRepo.add_subscription(session, user_id, channel, channel_id)

    await message.answer(msg)


@router.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: Message, tg_reader: TelegramReader, db_session_factory: SessionFactory) -> None:
    raw_channel = _parse_channel(message.text)
    if not raw_channel:
        await message.answer("Формат: /unsubscribe <channelNick/channelUrl>\nПример: /unsubscribe @durov")
        return

    channel = normalize_channel_identifier(raw_channel)

    try:
        channel_id = await tg_reader.resolve_channel_id(channel)
    except Exception:
        await message.answer("Не получилось распознать канал. Проверьте ссылку/ник.")
        return

    user_id = message.from_user.id

    async with db_session_factory() as session:
        async with session.begin():
            removed = await SubscriptionRepo.remove_subscription(session, user_id, channel_id)

    await message.answer("Отписка выполнена." if removed else "Вы не были подписаны на этот канал.")
