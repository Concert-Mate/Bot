import random
from dataclasses import dataclass
from datetime import date
from enum import Enum, IntEnum


class UserRegistrateCodes(Enum):
    SUCCESS = 0
    USER_ALREADY_EXISTS = 1
    NO_CONNECTION = 2
    INTERNAL_SERVER_ERROR = 3


@dataclass
class UserRegistrationResponse:
    code: UserRegistrateCodes
    registration_date: str


def __get_user_registration_response(code: int, registration_date: str) -> UserRegistrationResponse:
    return UserRegistrationResponse(code=UserRegistrateCodes(code), registration_date=registration_date)


__user_registration_codes_map = {
    0: __get_user_registration_response,
    1: __get_user_registration_response,
    2: __get_user_registration_response,
    3: __get_user_registration_response
}


class AddCityCodes(IntEnum):
    SUCCESS = 0
    CITY_NOT_EXIST = 1
    CITY_IS_FUZZ = 2
    CITY_ALREADY_ADDED = 3
    USER_NOT_FOUND = 4
    NO_CONNECTION = 5
    INTERNAL_SERVER_ERROR = 6


@dataclass
class AddCityResponse:
    code: AddCityCodes
    city_name: str


def __get_add_city_response(code: int, city: str) -> AddCityResponse:
    return AddCityResponse(code=AddCityCodes(code), city_name=city)


__add_city_codes_map = {
    0: __get_add_city_response,
    1: __get_add_city_response,
    2: __get_add_city_response,
    3: __get_add_city_response,
    4: __get_add_city_response,
    5: __get_add_city_response,
    6: __get_add_city_response
}


class AddPlaylistCodes(IntEnum):
    SUCCESS = 0
    INVALID_LINK = 1
    LINK_ALREADY_ADDED = 2
    USER_NOT_FOUND = 3
    NO_CONNECTION = 4
    INTERNAL_SERVER_ERROR = 5


@dataclass
class AddPlaylistResponse:
    code: AddPlaylistCodes


def __get_add_playlist_response(code: int) -> AddPlaylistResponse:
    return AddPlaylistResponse(code=AddPlaylistCodes(code))


__add_playlist_codes_map = {
    0: __get_add_playlist_response,
    1: __get_add_playlist_response,
    2: __get_add_playlist_response,
    3: __get_add_playlist_response,
    4: __get_add_playlist_response,
    5: __get_add_playlist_response,
}


def register_user(telegram_id: int) -> UserRegistrationResponse:
    # TODO: обращение к бэку
    luck_factor = random.randint(0, 2)
    reg_date = ''
    if luck_factor == 1:
        reg_date = date.today().isoformat()
    if luck_factor not in __user_registration_codes_map.keys():
        raise ValueError(f'Invalid response_code: {luck_factor}')
    return __user_registration_codes_map[luck_factor](luck_factor, reg_date)


def add_city(telegram_id: int, city: str) -> AddCityResponse:
    # TODO: обращение к бэку
    luck_factor = random.randint(0, 3)
    city_variant = ''
    if luck_factor == 3:
        city_variant = 'Челябинск'
    if luck_factor not in __add_city_codes_map.keys():
        raise ValueError(f'Invalid response_code: {luck_factor}')
    return __add_city_codes_map[luck_factor](luck_factor, city_variant)


def add_playlist(telegram_id: int, link: str) -> AddPlaylistResponse:
    # TODO: обращение к бэку
    luck_factor = random.randint(0, 1)
    if luck_factor not in __add_city_codes_map.keys():
        raise ValueError(f'Invalid response_code: {luck_factor}')
    return __add_playlist_codes_map[luck_factor](luck_factor)
