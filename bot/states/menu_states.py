from aiogram.fsm.state import StatesGroup, State


class MenuStates(StatesGroup):
    MAIN_MENU = State()
    CHANGE_DATA = State()
    HELP = State()
    HELP_DEAD_END = State()
    USER_INFO = State()
    USER_INFO_DEAD_END = State()
    TOOLS = State()
    MANAGING_NOTIFICATIONS = State()
    CONCERTS_SHOW = State()
    WAITING = State()

