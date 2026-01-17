from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

async def safe_delete(message: Message | None) -> None:
    if not message:
        return
    try:
        await message.delete()
    except TelegramBadRequest:
        # например: message to delete not found / can't be deleted
        pass
