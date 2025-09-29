from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from texts import WELCOME_TEXT, HELP_TEXT, CHOOSE_FLOW_TEXT
from keyboards import flow_keyboard, categories_keyboard
from states import JoinFlow
from config import START_FEED_CHAT_ID
from utils import user_link

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    # одно сообщение: приветствие + объяснение + клавиатура
    combined = f"{WELCOME_TEXT}{CHOOSE_FLOW_TEXT}"
    await message.answer(combined, reply_markup=flow_keyboard())
    await state.set_state(JoinFlow.waiting_flow)

    # уведомление во вторую группу
    if START_FEED_CHAT_ID:
        try:
            if message.from_user.username:
                username_or_link = f"@{message.from_user.username}"
            else:
                username_or_link = user_link(message.from_user, "профиль")

            feed_text = (
                "📣 Новый отклик: /start\n"
                f"Имя: {message.from_user.full_name}\n"
                f"Контакт: {username_or_link}\n"
            )
            await message.bot.send_message(chat_id=START_FEED_CHAT_ID, text=feed_text)
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление о старте: {e}")


@router.callback_query(F.data.startswith("flow:"))
async def on_flow_chosen(callback: types.CallbackQuery, state: FSMContext):
    flow = callback.data.split("flow:", 1)[1]
    if flow not in ("slavic", "hybrid"):
        await callback.answer("Неизвестный поток.", show_alert=True)
        return

    await state.update_data(flow=flow)
    await callback.message.edit_text(
        "Отлично! Теперь выбери раздел служения:",
        reply_markup=categories_keyboard()
    )
    await state.set_state(JoinFlow.waiting_category)
    await callback.answer()


@router.callback_query(F.data == "back:flow")
async def on_back_to_flow(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(flow=None)
    combined = f"{WELCOME_TEXT}\n\n{CHOOSE_FLOW_TEXT}"
    await callback.message.edit_text(combined, reply_markup=flow_keyboard())
    await state.set_state(JoinFlow.waiting_flow)
    await callback.answer()
