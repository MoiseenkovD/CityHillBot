from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states import JoinFlow
from texts import ASK_FULLNAME_TEXT, AFTER_FULLNAME_TEXT, PHONE_NOT_RECOGNIZED, THANKS_SENT
from keyboards import contact_request_kb
from utils import extract_phone, user_link
from data import CATEGORY_TITLES
from config import TARGET_CHAT_ID

router = Router()


@router.callback_query(F.data == "apply:selected")
async def on_apply_selected(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    department = data.get("department")
    if not department:
        await callback.answer("Сначала выберите служение.", show_alert=True)
        return

    await callback.message.answer(ASK_FULLNAME_TEXT)
    await state.set_state(JoinFlow.waiting_fullname)
    await callback.answer()


@router.message(JoinFlow.waiting_fullname, F.text)
async def on_fullname(message: types.Message, state: FSMContext):
    full_name = " ".join(message.text.split())
    if len(full_name) < 2:
        await message.answer("Имя слишком короткое. Напиши, пожалуйста, имя и фамилию.")
        return

    await state.update_data(full_name=full_name)
    await message.answer(
        AFTER_FULLNAME_TEXT.format(full_name=full_name),
        reply_markup=contact_request_kb()
    )
    await state.set_state(JoinFlow.waiting_contact)


@router.message(JoinFlow.waiting_contact, F.contact)
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

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else user_link(message.from_user, f"{message.from_user.full_name}")
    )
    phone = contact.phone_number

    text_for_group = (
        "<b>Новая заявка на служение</b>\n"
        f"Раздел: <b>{category_title}</b>\n"
        f"Служение: <b>{department}</b>\n"
        f"Имя (введено): <b>{full_name}</b>\n"
        f"Username: {username}\n"
        f"Телефон: <code>{phone}</code>\n"
        f"Комментарий: {contact_owner}"
    )
    try:
        await message.bot.send_message(chat_id=TARGET_CHAT_ID, text=text_for_group)
    except Exception as e:
        await message.answer(
            "Не удалось отправить заявку в группу. Сообщи администратору.\n"
            f"Техническая справка: <code>{e}</code>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return

    await message.answer(THANKS_SENT, reply_markup=ReplyKeyboardRemove())
    await state.clear()


@router.message(JoinFlow.waiting_contact, F.text)
async def on_contact_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    department = data.get("department", "—")
    category_key = data.get("category_key")
    category_title = CATEGORY_TITLES.get(category_key, "—")
    full_name = data.get("full_name") or message.from_user.full_name

    phone = extract_phone(message.text)
    if not phone:
        await message.answer(PHONE_NOT_RECOGNIZED, reply_markup=contact_request_kb())
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
        await message.bot.send_message(chat_id=TARGET_CHAT_ID, text=text_for_group)
    except Exception as e:
        await message.answer(
            "Не удалось отправить заявку в группу. Сообщи администратору.\n"
            f"Техническая справка: <code>{e}</code>",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        return

    await message.answer(THANKS_SENT, reply_markup=ReplyKeyboardRemove())
    await state.clear()
