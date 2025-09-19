from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from data import CATEGORY_TITLES, DEPARTMENTS_BY_CATEGORY  # ← абсолютный импорт


def categories_keyboard(cols: int = 2) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=title, callback_data=f"cat:{key}")
        for key, title in CATEGORY_TITLES.items()
    ]
    rows = [buttons[i:i+cols] for i in range(0, len(buttons), cols)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def departments_keyboard(category_key: str, cols: int = 2) -> InlineKeyboardMarkup:
    items = DEPARTMENTS_BY_CATEGORY.get(category_key, [])
    buttons = [InlineKeyboardButton(text=name, callback_data=f"dept:{name}") for name in items]
    rows = [buttons[i:i+cols] for i in range(0, len(buttons), cols)]
    rows.append([InlineKeyboardButton(text="⬅️ Back to categories", callback_data="back:categories")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def dept_apply_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подать заявку", callback_data="apply:selected")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back:depts")],
    ])


def contact_request_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)],
            [KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Нажмите, чтобы отправить номер телефона"
    )
