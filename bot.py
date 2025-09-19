import asyncio
import os
import re
from typing import Dict, List, Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")  # основная группа для заявок
START_FEED_CHAT_ID = os.getenv("START_FEED_CHAT_ID")  # вторая группа для уведомлений о старте (опционально)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")
if not TARGET_CHAT_ID:
    raise ValueError("TARGET_CHAT_ID не найден в .env")

TARGET_CHAT_ID = int(TARGET_CHAT_ID)

# Опциональный канал для уведомлений о старте
if START_FEED_CHAT_ID:
    try:
        START_FEED_CHAT_ID = int(START_FEED_CHAT_ID)
    except ValueError:
        START_FEED_CHAT_ID = None


WELCOME_TEXT = (
    "👋 Привет!\n"
    "Мы рады, что ты заинтересовался(ась) в том, чтобы стать частью команды волонтёров CityHill!\n\n"
    "В нашей церкви служение – это не просто помощь, а возможность быть проводником Божьей любви "
    "и благословением для других.\n"
    "✨ Каждый волонтёр — важная часть большой семьи CityHill.\n\n"
    "Здесь ты сможешь:\n"
    "🔹 Послужить своими талантами и временем\n"
    "🔹 Найти новых друзей и единомышленников\n"
    "🔹 Расти духовно и лично\n\n"
    "Если ты готов(а) сделать шаг — выбери направление, в котором хотел(а) бы служить, и мы свяжемся с тобой 🙏"
)

CATEGORY_TITLES: Dict[str, str] = {
    "worship":      "🎤 Worship",
    "kids":         "👶 Kids",
    "youth":        "🔥 Youth | Teens",
    "media":        "🎥 Media",
    "welcome":      "🤝 Welcome Service",
    "hospitality":  "🥗 Hospitality",
    "discover":     "✨ Discover Your Calling",
}

CATEGORY_HEADLINES: Dict[str, str] = {
    "discover": (
        "Иногда бывает непросто понять, где именно служить и какое направление выбрать. "
        "Но не переживайте — вы не одни! Наши лидеры с радостью помогут вам открыть ваши дары "
        "и найти то служение, где вы сможете приносить наибольшую радость и пользу."
    ),
    "worship":     "Будь частью команды, которая ведёт людей в Божье присутствие!",
    "kids":        "Вложи своё сердце в будущее поколение!",
    "youth":       "Помогай молодым раскрывать свой потенциал и строить жизнь с Богом!",
    "media":       "Твори, вдохновляй и делись Божьим словом через современные медиа!",
    "welcome":     "Стань тем, кто встречает людей с теплом и любовью!",
    "hospitality": "Служи людям через простые, но очень важные вещи — еду, кофе и уют.",
}

# Для discover нет отделов — после выбора категории сразу показываем кнопку "Подать заявку"
DEPARTMENTS_BY_CATEGORY: Dict[str, List[str]] = {
    "worship": ["Singers", "Musicians"],
    "kids": ["Sunday school", "ICan (special kids)"],
    "youth": ["Chosen Gen", "Teens (Slavic)"],
    "media": ["Audio", "Live stream video", "Lights", "Production / Social", "Photography", "Graphic Design"],
    "welcome": ["Welcome Center", "Red Carpet", "Info Booth", "Ushers"],
    "hospitality": ["Coffee shop", "Kitchen"],
}

DEPT_DESCRIPTIONS_BY_CATEGORY: Dict[str, Dict[str, str]] = {
    # discover без отделов — описание выше, в тексте категории
    "worship": {
        "Singers": "используй свой голос, чтобы вдохновлять и поклоняться.",
        "Musicians": "твои ноты и аккорды оживляют атмосферу хвалы.",
    },
    "kids": {
        "Sunday school": "помоги детям познавать Библию с радостью.",
        "ICan (special kids)": "будь светом и поддержкой для особенных детей.",
    },
    "youth": {
        "Chosen Gen": "поддержи новое поколение в вере и лидерстве.",
        "Teens (Slavic)": "будь рядом с подростками, помогая им идти Божьим путём.",
    },
    "media": {
        "Audio": "создай качественный звук для поклонения и проповеди.",
        "Live stream video": "помоги транслировать служение людям по всему миру.",
        "Lights": "добавь атмосферы и красоты через свет.",
        "Production / Social": "делись событиями церкви и вдохновляй онлайн.",
        "Photography": "запечатли живые моменты Божьей работы.",
        "Graphic Design": "используй творчество, чтобы донести послание.",
    },
    "welcome": {
        "Welcome Center": "будь первой улыбкой для гостей церкви.",
        "Red Carpet": "подари каждому ощущение праздника.",
        "Info Booth": "помоги найти ответы и почувствовать себя дома.",
        "Ushers": "создай атмосферу порядка и заботы во время служения.",
    },
    "hospitality": {
        "Coffee shop": "сделай чашку кофе местом общения и радости.",
        "Kitchen": "готовь с любовью и корми, как для семьи.",
    },
}

PHONE_RE = re.compile(r"\+?\d[\d\-\s\(\)]{8,}")

def extract_phone(text: str) -> Optional[str]:
    if not text:
        return None
    m = PHONE_RE.search(text)
    if not m:
        return None
    raw = m.group(0)
    has_plus = raw.strip().startswith("+")
    digits = re.sub(r"\D", "", raw)
    if len(digits) < 9:
        return None
    return f"+{digits}" if has_plus else digits

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

def build_category_description_text(category_key: str) -> str:
    title = CATEGORY_TITLES.get(category_key, "—")
    head = CATEGORY_HEADLINES.get(category_key, "")
    return f"{title}\n{head}"

def build_dept_description_text(category_key: str, department: str) -> str:
    cat_title = CATEGORY_TITLES.get(category_key, "—")
    head = CATEGORY_HEADLINES.get(category_key, "")
    desc = DEPT_DESCRIPTIONS_BY_CATEGORY.get(category_key, {}).get(department, "")
    top = f"{cat_title}\n{head}" if head else cat_title
    middle = f"• <b>{department}</b> — {desc}" if desc else f"• <b>{department}</b>"
    return f"{top}\n\n{middle}\n\nГотов(а) присоединиться? Нажми кнопку ниже 👇"

class JoinFlow(StatesGroup):
    waiting_category = State()
    waiting_department = State()
    waiting_apply = State()
    waiting_fullname = State()
    waiting_contact = State()

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=categories_keyboard())
    await state.set_state(JoinFlow.waiting_category)

    # --- Уведомление во вторую группу об отклике на /start (если настроено) ---
    if START_FEED_CHAT_ID:
        try:
            username = f"@{message.from_user.username}" if message.from_user.username else "(нет username)"
            # Без HTML-тегов, чтобы не париться с экранированием имени
            feed_text = (
                "📣 Новый отклик: /start\n"
                f"Имя: {message.from_user.full_name}\n"
                f"Username: {username}\n"
                f"User ID: {message.from_user.id}\n"
            )
            await bot.send_message(chat_id=START_FEED_CHAT_ID, text=feed_text)
        except Exception as e:
            # Тихо игнорируем ошибку, чтобы не мешать основному сценарию
            print(f"[WARN] Не удалось отправить уведомление о старте: {e}")

@dp.callback_query(F.data.startswith("cat:"))
async def on_category_chosen(callback: types.CallbackQuery, state: FSMContext):
    cur = await state.get_state()
    if cur not in (JoinFlow.waiting_category, JoinFlow.waiting_department, JoinFlow.waiting_apply):
        await callback.answer("Начни с /start, чтобы выбрать служение.", show_alert=True)
        return

    category_key = callback.data.split("cat:", 1)[1]
    if category_key not in CATEGORY_TITLES:
        await callback.answer("Неизвестный раздел.", show_alert=True)
        return

    await state.update_data(category_key=category_key)

    # Особая логика для discover: описание + кнопка "Подать заявку"
    if category_key == "discover":
        await state.update_data(department="Discover consultation")  # виртуальное служение для заявки
        text = build_category_description_text(category_key)
        await callback.message.edit_text(text, reply_markup=dept_apply_keyboard())
        await state.set_state(JoinFlow.waiting_apply)
        await callback.answer()
        return

    # Обычный путь для остальных категорий
    text = build_category_description_text(category_key)
    await callback.message.edit_text(text, reply_markup=departments_keyboard(category_key))
    await state.set_state(JoinFlow.waiting_department)
    await callback.answer()

@dp.callback_query(F.data == "back:categories")
async def on_back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=categories_keyboard())
    await state.set_state(JoinFlow.waiting_category)
    await callback.answer()

@dp.callback_query(F.data.startswith("dept:"))
async def on_department_chosen(callback: types.CallbackQuery, state: FSMContext):
    if await state.get_state() != JoinFlow.waiting_department:
        await callback.answer("Сначала выбери раздел через /start.", show_alert=True)
        return

    department = callback.data.split("dept:", 1)[1]
    data = await state.get_data()
    category_key = data.get("category_key")

    valid_list = DEPARTMENTS_BY_CATEGORY.get(category_key, [])
    if department not in valid_list:
        await callback.answer("Выбранное служение не относится к этому разделу.", show_alert=True)
        return

    await state.update_data(department=department)
    text = build_dept_description_text(category_key, department)
    await callback.message.edit_text(text, reply_markup=dept_apply_keyboard())
    await state.set_state(JoinFlow.waiting_apply)
    await callback.answer()

@dp.callback_query(F.data == "back:depts")
async def on_back_to_depts(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_key = data.get("category_key")
    if not category_key:
        await callback.answer("Нет активного раздела. Нажмите /start.", show_alert=True)
        return

    # Для discover возвращаемся к списку категорий (там нет отделов)
    if category_key == "discover":
        await callback.message.edit_text(WELCOME_TEXT, reply_markup=categories_keyboard())
        await state.set_state(JoinFlow.waiting_category)
        await callback.answer()
        return

    text = build_category_description_text(category_key)
    await callback.message.edit_text(text, reply_markup=departments_keyboard(category_key))
    await state.set_state(JoinFlow.waiting_department)
    await callback.answer()

@dp.callback_query(F.data == "apply:selected")
async def on_apply_selected(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    department = data.get("department")
    if not department:
        await callback.answer("Сначала выберите служение.", show_alert=True)
        return

    await callback.message.answer(
        "Пожалуйста, напиши <b>своё имя и фамилию</b> одним сообщением.\n"
        "Например: <code>Ivan Petrov</code> или <code>Иван Петров</code>.\n\n"
        "Можно написать «Отмена», чтобы прервать."
    )
    await state.set_state(JoinFlow.waiting_fullname)
    await callback.answer()

@dp.message(F.text.casefold() == "отмена")
async def cancel_any(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отменено. Если захочешь начать заново — напиши /start.",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(JoinFlow.waiting_fullname, F.text)
async def on_fullname(message: types.Message, state: FSMContext):
    full_name = " ".join(message.text.split())
    if len(full_name) < 2:
        await message.answer("Имя слишком короткое. Напиши, пожалуйста, имя и фамилию.")
        return

    await state.update_data(full_name=full_name)
    await message.answer(
        f"Спасибо, {full_name}! Теперь, пожалуйста, поделись своим контактом (телефоном) "
        "или отправь номер вручную.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)],
                [KeyboardButton(text="Отмена")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Нажмите, чтобы отправить номер телефона"
        )
    )
    await state.set_state(JoinFlow.waiting_contact)

@dp.message(JoinFlow.waiting_contact, F.contact)
async def on_contact_shared(message: types.Message, state: FSMContext):
    data = await state.get_data()
    department = data.get("department", "—")
    category_key = data.get("category_key")
    category_title = CATEGORY_TITLES.get(category_key, "—")
    full_name = data.get("full_name") or message.from_user.full_name

    contact = message.contact
    contact_owner = (
        "сам(а) отправил(а) свой контакт"
        if contact.user_id == message.from_user.id
        else f"передал(а) контакт: {contact.first_name or ''} {contact.last_name or ''}".strip()
    )

    username = f"@{message.from_user.username}" if message.from_user.username else "(нет username)"
    phone = contact.phone_number

    text_for_group = (
        "<b>Новая заявка на служение</b>\n"
        f"Раздел: <b>{category_title}</b>\n"
        f"Служение: <b>{department}</b>\n"
        f"Имя (введено): <b>{full_name}</b>\n"
        f"Username: {username}\n"
        f"User ID: <code>{message.from_user.id}</code>\n"
        f"Телефон: <code>{phone}</code>\n"
        f"Комментарий: {contact_owner}"
    )
    try:
        await bot.send_message(chat_id=TARGET_CHAT_ID, text=text_for_group)
    except Exception as e:
        await message.answer(
            "Не удалось отправить заявку в группу. Сообщи администратору.\n"
            f"Техническая справка: <code>{e}</code>",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()
        return

    await message.answer(
        "Спасибо! Контакт получен и заявка отправлена ответственным 🙌\n"
        "Мы свяжемся с тобой в ближайшее время.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()

@dp.message(JoinFlow.waiting_contact, F.text)
async def on_contact_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    department = data.get("department", "—")
    category_key = data.get("category_key")
    category_title = CATEGORY_TITLES.get(category_key, "—")
    full_name = data.get("full_name") or message.from_user.full_name

    phone = extract_phone(message.text)
    if not phone:
        await message.answer(
            "Похоже, номер не распознан 🤔\n"
            "Пришли его целиком: <code>+1 (425) 563-0696</code> или <code>380939424247</code>\n\n"
            "Или нажми «📱 Поделиться контактом».",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)],
                    [KeyboardButton(text="Отмена")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Нажмите, чтобы отправить номер телефона"
            )
        )
        return

    username = f"@{message.from_user.username}" if message.from_user.username else "(нет username)"

    text_for_group = (
        "<b>Новая заявка на служение</b>\n"
        f"Раздел: <b>{category_title}</b>\n"
        f"Служение: <b>{department}</b>\n"
        f"Имя (введено): <b>{full_name}</b>\n"
        f"Username: {username}\n"
        f"Телефон: <code>{phone}</code>"
    )
    try:
        await bot.send_message(chat_id=TARGET_CHAT_ID, text=text_for_group)
    except Exception as e:
        await message.answer(
            "Не удалось отправить заявку в группу. Сообщи администратору.\n"
            f"Техническая справка: <code>{e}</code>",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.clear()
        return

    await message.answer(
        "Спасибо! Контакт получен и заявка отправлена ответственным 🙌\n"
        "Мы свяжемся с тобой в ближайшее время.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start — раздел → служение → Описание → Подать заявку → имя/фамилия → контакт\n"
        "/help — помощь"
    )

@dp.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(f"chat_id этого чата: <code>{message.chat.id}</code>")

async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


