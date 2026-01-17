from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.db.di import SessionFactory
from app.db.repositories.subscriptions import SubscriptionRepo

router = Router()


@router.message(Command("list"))
async def cmd_list(message: Message, db_session_factory: SessionFactory) -> None:
    user_id = message.from_user.id

    async with db_session_factory() as session:
        subs = await SubscriptionRepo.list_subscriptions(session, user_id)

    if not subs:
        await message.answer("У вас пока нет подписок. Добавьте: /subscribe @channel")
        return

    lines = ["Ваши подписки:"]
    for i, s in enumerate(subs, start=1):
        # channel_identifier у нас уже нормализованный (обычно без @)
        ident = s.channel_identifier
        if not ident.startswith("@"):
            ident = "@" + ident
        lines.append(f"{i}) {ident}")

    await message.answer("\n".join(lines))
