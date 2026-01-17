from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

HELP_TEXT = (
    "Команды:\n"
    "/summary [channelNick/channelUrl] [n] — суммаризация последних n постов\n"
    "/themes  [channelNick/channelUrl] [n] — темы/тезисы по последним n постам\n"
    "/subscribe [channelNick/channelUrl] — добавить канал в список (лимит 10)\n"
    "/unsubscribe [channelNick/channelUrl] — убрать канал из списка\n"
    "/help — помощь\n\n"
    "Примеры:\n"
    "/summary @durov 10\n"
    "/themes https://t.me/durov 20\n"
)

@router.message(Command("help", "start"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)
