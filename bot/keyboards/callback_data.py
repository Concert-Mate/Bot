from enum import StrEnum


class KeyboardCallbackData(StrEnum):
    CANCEL = 'cancel'
    BACK = 'back'
    ADD_CITY = 'add_city'
    SHOW_CONCERTS = 'show_concerts'
    APPLY = 'apply'
    DENY = 'deny'
    CITIES = 'cities'
    LINKS = 'links'
    DEVELOPMENT_COMMUNICATION = 'dev_comm'
    MAIN_INFO = 'main_info'
    CHANGE_DATA = 'change_data'
    TOOLS = 'tools'
    FAQ = 'faq'
    REMOVE_CITY = 'remove_city'
    REMOVE_LINK = 'remove_link'
    ADD_LINK = 'add_link'
    USER_INFO = 'user_info'
    ENABLE = 'enable'
    DISABLE = 'disable'
    NOTICE_MANAGEMENT = 'notice_management'
