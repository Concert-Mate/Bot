from aiogram.fsm.state import StatesGroup, State


class MenuStates(StatesGroup):
    MAIN_MENU = State()
    CHANGE_DATA = State()
    FAQ = State()
    FAQ_DEAD_END = State()
