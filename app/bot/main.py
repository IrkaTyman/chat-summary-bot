import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import load_config
from app.bot.handlers.help import router as help_router


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    config = load_config()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    dp.include_router(help_router)

    # Важно: drop_pending_updates=True, чтобы не разгребать старые апдейты
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
