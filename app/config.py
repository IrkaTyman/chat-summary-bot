import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    tg_api_id: int
    tg_api_hash: str
    tg_session_name: str
    database_url: str

def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Create .env and set BOT_TOKEN.")

    api_id = os.getenv("TG_API_ID")
    api_hash = os.getenv("TG_API_HASH")
    session_name = os.getenv("TG_SESSION_NAME", "telethon")

    if not api_id or not api_hash:
        raise RuntimeError("TG_API_ID/TG_API_HASH are not set in .env")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set in .env")

    return Config(
        bot_token=token,
        tg_api_id=int(api_id),
        tg_api_hash=api_hash,
        tg_session_name=session_name,
        database_url=db_url,
    )
