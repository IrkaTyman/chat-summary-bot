import asyncio
import logging
import os
import getpass

import qrcode
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from app.config import load_config


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    cfg = load_config()
    client = TelegramClient(cfg.tg_session_name, cfg.tg_api_id, cfg.tg_api_hash)

    await client.connect()

    if await client.is_user_authorized():
        print("Telethon: уже авторизован, ничего делать не нужно.")
        await client.disconnect()
        return

    qr_login = await client.qr_login()

    print("Откройте Telegram на телефоне:")
    print("Settings -> Devices -> Link Desktop Device")
    print("и отсканируйте QR ниже.\n")

    qr = qrcode.QRCode(border=1)
    qr.add_data(qr_login.url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

    print("\nЖду подтверждения логина в Telegram…")

    try:
        await qr_login.wait()
    except SessionPasswordNeededError:
        pwd = os.getenv("TG_2FA_PASSWORD") or getpass.getpass("Введите пароль 2FA: ")
        await client.sign_in(password=pwd)

    print("Готово: авторизация успешна, сессия сохранена.")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
