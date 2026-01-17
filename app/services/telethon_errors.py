from telethon.errors import (
    ChannelPrivateError,
    ChatAdminRequiredError,
    FloodWaitError,
    UsernameInvalidError,
    UsernameNotOccupiedError,
)


def humanize_telethon_error(e: Exception) -> str:
    if isinstance(e, UsernameNotOccupiedError):
        return "Канал не найден. Проверьте ник/ссылку."
    if isinstance(e, UsernameInvalidError):
        return "Некорректный ник/ссылка на канал."
    if isinstance(e, (ChannelPrivateError, ChatAdminRequiredError)):
        return "Нет доступа к каналу (возможно приватный или требуется доступ)."
    if isinstance(e, FloodWaitError):
        return f"Слишком много запросов к Telegram. Попробуйте позже (ожидание ~{e.seconds} сек)."
    return "Не удалось получить данные канала. Попробуйте позже."
