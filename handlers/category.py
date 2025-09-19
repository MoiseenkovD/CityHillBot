from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from data import CATEGORY_TITLES, build_category_description_text, DEPARTMENTS_BY_CATEGORY, build_dept_description_text
from keyboards import departments_keyboard, dept_apply_keyboard, categories_keyboard
from texts import WELCOME_TEXT
from states import JoinFlow

router = Router()


@router.callback_query(F.data.startswith("cat:"))
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

    # Discover: сразу описание + кнопка "Подать заявку"
    if category_key == "discover":
        await state.update_data(department="Discover consultation")  # виртуальное служение
        text = build_category_description_text(category_key)
        await callback.message.edit_text(text, reply_markup=dept_apply_keyboard())
        await state.set_state(JoinFlow.waiting_apply)
        await callback.answer()
        return

    text = build_category_description_text(category_key)
    await callback.message.edit_text(text, reply_markup=departments_keyboard(category_key))
    await state.set_state(JoinFlow.waiting_department)
    await callback.answer()


@router.callback_query(F.data == "back:categories")
async def on_back_to_categories(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=categories_keyboard())
    await state.set_state(JoinFlow.waiting_category)
    await callback.answer()


@router.callback_query(F.data.startswith("dept:"))
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


@router.callback_query(F.data == "back:depts")
async def on_back_to_depts(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_key = data.get("category_key")
    if not category_key:
        await callback.answer("Нет активного раздела. Нажмите /start.", show_alert=True)
        return

    if category_key == "discover":
        await callback.message.edit_text(WELCOME_TEXT, reply_markup=categories_keyboard())
        await state.set_state(JoinFlow.waiting_category)
        await callback.answer()
        return

    text = build_category_description_text(category_key)
    await callback.message.edit_text(text, reply_markup=departments_keyboard(category_key))
    await state.set_state(JoinFlow.waiting_department)
    await callback.answer()
