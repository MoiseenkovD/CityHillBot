from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states import JoinFlow
from texts import ASK_FULLNAME_TEXT, AFTER_FULLNAME_TEXT, PHONE_NOT_RECOGNIZED, THANKS_SENT
from keyboards import contact_request_kb
from utils import normalize_us_phone, user_link
from data import CATEGORY_TITLES
from config import select_target_chat_id

router = Router()


@router.callback_query(F.data == "apply:selected")
async def on_apply_selected(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    department = data.get("department")
    category_key = data.get("category_key")
    flow = data.get("flow")

    # поток обязателен для всех сценариев теперь (включая discover)
    if not flow:
        await callback.answer("Сначала выбери поток: /start", show_alert=True)
        return

    if not department:
        await callback.answer("Сначала выбери служение.", show_alert=True)
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


def _username_or_profile(u: types.User) -> str:
    """Если есть username — вернём @username, иначе ссылку tg://user?id=..."""
    return f"@{u.username}" if u.username else user_link(u, "профиль")


async def _send_application(
    bot,
    chat_id: int,
    *,
    category_title: str,
    department: str,
    full_name: str,
    from_user: types.User,
    phone: str,
    contact_owner: str,
    flow: str
):
    flow_line = f"Поток: <b>{'Slavic' if flow == 'slavic' else 'Hybrid'}</b>\n"
    text_for_group = (
        "<b>Новая заявка на служение</b>\n"
        f"{flow_line}"
        f"Раздел: <b>{category_title}</b>\n"
        f"Служение: <b>{department}</b>\n"
        f"Имя (введено): <b>{full_name}</b>\n"
        f"Контакт: {_username_or_profile(from_user)}\n"
        f"Телефон: <code>{phone}</code>\n"
        f"Комментарий: {contact_owner}"
    )
    await bot.send_message(chat_id=chat_id, text=text_for_group)


@router.message(JoinFlow.waiting_contact, F.contact)
async def on_contact_shared(message: types.Message, state: FSMContext):
    data = await state.get_data()
    department = data.get("department", "—")
    category_key = data.get("category_key")
    category_title = CATEGORY_TITLES.get(category_key, "—")
    full_name = data.get("full_name") or message.from_user.full_name
    flow = data.get("flow")

    contact = message.contact
    contact_owner = (
        "сам(а) отправил(а) свой контакт"
        if contact.user_id == message.from_user.id
        else f"передал(а) контакт: {contact.first_name or ''} {contact.last_name or ''}".strip()
    )

    # строгая валидация только для номеров США
    phone = normalize_us_phone(contact.phone_number)
    if not phone:
        await message.answer(PHONE_NOT_RECOGNIZED, reply_markup=contact_request_kb())
        return

    target_chat_id = select_target_chat_id(flow)

    try:
        await _send_application(
            message.bot,
            target_chat_id,
            category_title=category_title,
            department=department,
            full_name=full_name,
            from_user=message.from_user,
            phone=phone,
            contact_owner=contact_owner,
            flow=flow,
        )
    except Exception as e:
        await message.answer(
            "Не удалось отправить заявку в группу. Сообщи администратору.\n"
            f"Техническая справка: <code>{e}</code>",
            reply_markup=ReplyKeyboardRemove(),
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
    flow = data.get("flow")

    # строгая валидация только для номеров США
    phone = normalize_us_phone(message.text)
    if not phone:
        await message.answer(PHONE_NOT_RECOGNIZED, reply_markup=contact_request_kb())
        return

    target_chat_id = select_target_chat_id(flow)

    try:
        await _send_application(
            message.bot,
            target_chat_id,
            category_title=category_title,
            department=department,
            full_name=full_name,
            from_user=message.from_user,
            phone=phone,
            contact_owner="ввел(а) номер вручную",
            flow=flow,
        )
    except Exception as e:
        await message.answer(
            "Не удалось отправить заявку в группу. Сообщи администратору.\n"
            f"Техническая справка: <code>{e}</code>",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
        return

    await message.answer(THANKS_SENT, reply_markup=ReplyKeyboardRemove())
    await state.clear()
