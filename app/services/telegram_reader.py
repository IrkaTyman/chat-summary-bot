from __future__ import annotations

import re
from dataclasses import dataclass

from telethon import TelegramClient
from telethon.tl.custom.message import Message


def normalize_channel_identifier(raw: str) -> str:
    s = raw.strip()
    s = re.sub(r"^https?://t\.me/", "", s)
    s = re.sub(r"^s/", "", s)
    s = s.strip("/")

    if s.startswith("@"):
        s = s[1:]

    s = s.split("?")[0].strip("/")
    return s


@dataclass
class Post:
    id: int
    text: str


class TelegramReader:
    def __init__(self, api_id: int, api_hash: str, session_name: str) -> None:
        self._client = TelegramClient(session_name, api_id, api_hash)

    async def start(self) -> None:
        await self._client.connect()
        if not await self._client.is_user_authorized():
            raise RuntimeError(
                "Telethon не авторизован. Запустите: python -m app.scripts.telethon_auth_qr"
            )

    async def close(self) -> None:
        await self._client.disconnect()

    async def get_last_posts(self, channel_identifier: str, limit: int) -> list[Post]:
        if limit <= 0:
            return []

        ident = normalize_channel_identifier(channel_identifier)
        entity = await self._client.get_entity(ident)
        messages: list[Message] = await self._client.get_messages(entity, limit=limit)

        posts: list[Post] = []
        for m in reversed(messages):  # старые -> новые
            text = (m.message or "").strip()
            if not text:
                text = "[пост без текста]"
            posts.append(Post(id=m.id, text=text))
        return posts
    
    async def resolve_channel_id(self, channel_identifier: str) -> int:
        ident = normalize_channel_identifier(channel_identifier)
        entity = await self._client.get_entity(ident)
        return int(entity.id)

