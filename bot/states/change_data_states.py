from aiogram.fsm.state import StatesGroup, State


class ChangeDataStates(StatesGroup):
    ENTER_NEW_CITY = State()
    CITY_NAME_IS_FUZZY = State()
    REMOVE_CITY = State()
    ENTER_NEW_PLAYLIST = State()
    REMOVE_PLAYLIST = State()
