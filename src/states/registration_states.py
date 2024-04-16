from aiogram.fsm.state import StatesGroup, State


class RegistrationStates(StatesGroup):
    ADD_FIRST_CITY = State()
    ADD_LINK = State()
    ADD_CITIES_IN_LOOP = State()
    ADD_CITY_CALLBACKS = State()
