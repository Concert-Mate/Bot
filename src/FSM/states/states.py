import enum

from telegram.ext import ConversationHandler

__all__ = ['GlobalStates', 'CityStates', 'END']


# /---------- GLOBAL FSM STATES ----------\

class GlobalStates(enum.Enum):
    REGISTRATION = '1'
    CITY_REGISTRATION = '2'
    CITY_REGISTRATION_CALLBACKS = '3'
    LINK_REGISTRATION = '4'
    IDLE = '5'
    STOPPING = '6'
    IDLE_CALLBACKS = '7'
    CHANGE_DATA_CALLBACKS = '8'


# /---------- CITY FSM STATES ----------\
class CityStates(enum.Enum):
    CONTINUE_ADD_CITIES = '11'
    STOP_ADD_CITIES = '12'
    APPLY_ADD_VARIANT = '13'
    DENY_ADD_VARIANT = '14'
    ADD_CITY = '15'


END = ConversationHandler.END
