from __future__ import annotations

def split_text(text: str, max_len: int = 3500) -> list[str]:
    """
    Telegram лимит ~4096 символов на сообщение. Берём безопасно 3500.
    Режем по переносам строк, если можно.
    """
    text = text.strip()
    if len(text) <= max_len:
        return [text]

    parts: list[str] = []
    buf: list[str] = []
    cur = 0

    for line in text.splitlines(keepends=True):
        if cur + len(line) > max_len and buf:
            parts.append("".join(buf).strip())
            buf = []
            cur = 0
        buf.append(line)
        cur += len(line)

    if buf:
        parts.append("".join(buf).strip())

    # fallback: если вдруг без переносов одна строка огромная
    fixed: list[str] = []
    for p in parts:
        if len(p) <= max_len:
            fixed.append(p)
        else:
            for i in range(0, len(p), max_len):
                fixed.append(p[i:i+max_len].strip())
    return [x for x in fixed if x]
