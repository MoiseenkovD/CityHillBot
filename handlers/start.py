from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from texts import WELCOME_TEXT, HELP_TEXT
from keyboards import categories_keyboard
from states import JoinFlow
from config import START_FEED_CHAT_ID
from utils import user_link

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=categories_keyboard())
    await state.set_state(JoinFlow.waiting_category)

    # Уведомление во вторую группу о запуске (если настроено)
    if START_FEED_CHAT_ID:
        try:
            if message.from_user.username:
                username_or_link = f"@{message.from_user.username}"
            else:
                username_or_link = user_link(message.from_user, f"{message.from_user.full_name}")

            feed_text = (
                "📣 Новый отклик: /start\n"
                f"Имя: {message.from_user.full_name}\n"
                f"Контакт: {username_or_link}\n"
            )

            await message.bot.send_message(chat_id=START_FEED_CHAT_ID, text=feed_text)
        except Exception as e:
            print(f"[WARN] Не удалось отправить уведомление о старте: {e}")


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(HELP_TEXT)


@router.message(Command("id"))
async def cmd_id(message: types.Message):
    await message.answer(f"chat_id этого чата: <code>{message.chat.id}</code>")


@router.message(F.text.casefold() == "отмена")
async def cancel_any(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено. Если захочешь начать заново — напиши /start.")
