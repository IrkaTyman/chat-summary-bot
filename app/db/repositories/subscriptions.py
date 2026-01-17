from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Subscription


class SubscriptionRepo:
    @staticmethod
    async def ensure_user(session: AsyncSession, telegram_user_id: int) -> None:
        exists = await session.scalar(
            select(func.count()).select_from(User).where(User.telegram_user_id == telegram_user_id)
        )
        if not exists:
            session.add(User(telegram_user_id=telegram_user_id))

    @staticmethod
    async def count_user_subscriptions(session: AsyncSession, telegram_user_id: int) -> int:
        return int(
            await session.scalar(
                select(func.count()).select_from(Subscription).where(Subscription.telegram_user_id == telegram_user_id)
            )
        )

    @staticmethod
    async def add_subscription(
        session: AsyncSession,
        telegram_user_id: int,
        channel_identifier: str,
        channel_id: int,
    ) -> tuple[bool, str]:
        """
        Returns (created, message)
        """
        # already exists?
        existing = await session.scalar(
            select(Subscription).where(
                Subscription.telegram_user_id == telegram_user_id,
                Subscription.channel_id == channel_id,
            )
        )
        if existing:
            return False, "Вы уже подписаны на этот канал."

        session.add(
            Subscription(
                telegram_user_id=telegram_user_id,
                channel_identifier=channel_identifier,
                channel_id=channel_id,
            )
        )
        return True, "Подписка добавлена."

    @staticmethod
    async def remove_subscription(session: AsyncSession, telegram_user_id: int, channel_id: int) -> bool:
        res = await session.execute(
            delete(Subscription).where(
                Subscription.telegram_user_id == telegram_user_id,
                Subscription.channel_id == channel_id,
            )
        )
        # rowcount может быть None в некоторых драйверах, но в asyncpg обычно ок
        return bool(res.rowcount)
    
    @staticmethod
    async def list_subscriptions(session: AsyncSession, telegram_user_id: int) -> list[Subscription]:
        res = await session.scalars(
            select(Subscription)
            .where(Subscription.telegram_user_id == telegram_user_id)
            .order_by(Subscription.created_at.asc())
        )
        return list(res)
