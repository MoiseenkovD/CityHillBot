import re
from typing import Optional
from aiogram import types


_US_10_DIGITS = re.compile(r"^\d{10}$")
_US_11_WITH_1 = re.compile(r"^1\d{10}$")
_US_PLUS = re.compile(r"^\+1\d{10}$")


def normalize_us_phone(text: str) -> Optional[str]:
    if not text:
        return None
    # убираем всё, кроме цифр и +
    raw = text.strip()
    digits = re.sub(r"\D", "", raw)

    if _US_10_DIGITS.match(digits):
        return f"+1{digits}"
    if _US_11_WITH_1.match(digits):
        return f"+{digits}"
    if _US_PLUS.match(raw.replace(" ", "")):
        return raw.replace(" ", "")
    return None


def user_link(user: types.User, label: Optional[str] = None) -> str:
    text = label or (user.full_name or "профиль")
    return f'<a href="tg://user?id={user.id}">{text}</a>'