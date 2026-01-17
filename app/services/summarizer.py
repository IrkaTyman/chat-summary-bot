from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from app.services.telegram_reader import Post


RU_STOPWORDS = {
    "и","в","во","не","что","он","на","я","с","со","как","а","то","все","она","так",
    "его","но","да","ты","к","у","же","вы","за","бы","по","только","ее","мне","было",
    "вот","от","меня","еще","нет","о","из","ему","теперь","когда","даже","ну","вдруг",
    "ли","если","уже","или","ни","быть","был","него","до","вас","нибудь","опять","уж",
    "вам","ведь","там","потом","себя","ничего","ей","может","они","тут","где","есть",
    "надо","ней","для","мы","тебя","их","чем","была","сам","чтоб","без","будто",
}

@dataclass(frozen=True)
class SummaryResult:
    title: str
    body: str


class SummarizerStub:
    """
    Заглушка: без LLM.
    Делает:
      - summary: 5-10 буллетов из первых строк постов
      - themes: топ-5 "тем" по частотности слов (очень грубо)
    """
    def summarize(self, posts: list[Post]) -> SummaryResult:
        bullets = []
        for p in posts[-10:]:  # берём максимум 10 последних для вывода
            t = re.sub(r"\s+", " ", p.text).strip()
            if not t or t == "[пост без текста]":
                continue
            bullets.append(self._clip(t, 180))
        if not bullets:
            bullets = ["Нет текстовых постов для суммаризации."]

        body = "Сводка по последним постам:\n" + "\n".join(f"• {b}" for b in bullets[:10])
        return SummaryResult(title="Саммари", body=body)

    def themes(self, posts: list[Post]) -> SummaryResult:
        text = " ".join(p.text for p in posts if p.text and p.text != "[пост без текста]")
        words = re.findall(r"[а-яА-ЯёЁ]{4,}", text.lower())
        words = [w for w in words if w not in RU_STOPWORDS]
        common = [w for w, _ in Counter(words).most_common(5)]

        if not common:
            common = ["нет_данных"]

        body = "Темы (заглушка):\n" + "\n".join(f"• {w}" for w in common)
        return SummaryResult(title="Темы", body=body)

    @staticmethod
    def _clip(s: str, n: int) -> str:
        return s if len(s) <= n else s[:n].rstrip() + "…"
