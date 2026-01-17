import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import load_config
from app.bot.handlers.help import router as help_router
from app.bot.handlers.summary import router as summary_router
from app.services.telegram_reader import TelegramReader
from app.db.session import make_engine, make_session_factory
from app.bot.handlers.subscribe import router as subscribe_router
from app.bot.handlers.list_subscriptions import router as list_router

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    config = load_config()
    engine = make_engine(config.database_url)
    session_factory = make_session_factory(engine)
    
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    tg_reader = TelegramReader(config.tg_api_id, config.tg_api_hash, config.tg_session_name)
    await tg_reader.start()
    dp["tg_reader"] = tg_reader
    dp["db_session_factory"] = session_factory

    dp.include_router(help_router)
    dp.include_router(summary_router)
    dp.include_router(subscribe_router)
    dp.include_router(list_router)

    try:
        await dp.start_polling(bot, drop_pending_updates=True)
    finally:
        await engine.dispose()
        await tg_reader.close()


if __name__ == "__main__":
    asyncio.run(main())
