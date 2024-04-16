import random
from dataclasses import dataclass
from datetime import date
from enum import IntEnum


class ResponseCodes(IntEnum):
    SUCCESS = 0
    INTERNAL_ERROR = 1
    USER_ALREADY_EXISTS = 2
    USER_NOT_FOUND = 3
    CITY_ALREADY_ADDED = 4
    CITY_NOT_ADDED = 5
    INVALID_CITY = 6
    FUZZY_CITY = 7
    TRACKS_LIST_ALREADY_ADDED = 8
    TRACKS_LIST_NOT_ADDED = 9
    INVALID_TRACKS_LIST = 10
    NO_CONNECTION = 11


__add_playlist_codes = [0, 1, 3, 8, 10, 11]
__user_registration_codes = [0, 1, 2, 11]
__add_city_codes = [0, 1, 3, 4, 6, 7, 11]


@dataclass
class UserRegistrationResponse:
    code: ResponseCodes
    registration_date: str


@dataclass
class AddCityResponse:
    code: ResponseCodes
    city_name: str


@dataclass
class AddPlaylistResponse:
    code: ResponseCodes


def register_user(telegram_id: int) -> UserRegistrationResponse:
    # TODO: обращение к бэку
    luck_factor = random.randint(0, 3)
    code = __user_registration_codes[luck_factor]
    reg_date = ''
    if code == 1:
        reg_date = date.today().isoformat()
    if code not in __user_registration_codes:
        raise ValueError(f'Invalid response_code: {code}')
    return UserRegistrationResponse(ResponseCodes(code), reg_date)


def add_city(telegram_id: int, city: str) -> AddCityResponse:
    # TODO: обращение к бэку
    luck_factor = random.randint(0, 3)
    code = __add_city_codes[luck_factor]
    city_variant = ''
    if code == 3:
        city_variant = 'Челябинск'
    if code not in __add_city_codes:
        raise ValueError(f'Invalid response_code: {code}')
    return AddCityResponse(ResponseCodes(code), city_variant)


def add_playlist(telegram_id: int, link: str) -> AddPlaylistResponse:
    # TODO: обращение к бэку
    luck_factor = random.randint(0, 1)
    code = __add_playlist_codes[luck_factor]
    if code not in __add_playlist_codes:
        raise ValueError(f'Invalid response_code: {code}')
    return AddPlaylistResponse(ResponseCodes(code))
