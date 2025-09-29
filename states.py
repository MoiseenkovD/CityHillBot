from aiogram.fsm.state import StatesGroup, State

class JoinFlow(StatesGroup):
    waiting_flow = State()        # СНАЧАЛА выбор Slavic/Hybrid
    waiting_category = State()
    waiting_department = State()
    waiting_apply = State()
    waiting_fullname = State()
    waiting_contact = State()
