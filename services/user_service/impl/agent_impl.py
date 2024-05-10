import logging
from typing import Optional

import aiohttp
from aiohttp import ClientConnectionError

from model import Concert
from model.playlist import Playlist
from .. import InternalErrorException, UserAlreadyExistsException, TrackListNotAddedException, \
    CityAlreadyAddedException, UserDoesNotExistException, InvalidCityException, FuzzyCityException, \
    CityNotAddedException, TrackListAlreadyAddedException, InvalidTrackListException
from ..agent import UserServiceAgent
from ..exceptions import InvalidCoordsException
from ..response import UserTrackListsResponse, UserCitiesResponse, UserConcertsResponse, DefaultResponse, \
    ResponseStatusCode, UserTrackListResponse
from ..response.user_add_city_response import UserAddCityResponse


class UserServiceAgentImpl(UserServiceAgent):
    __session: aiohttp.ClientSession
    
    __BAD_ANSWER_TEXT = 'Bad answer from backend'
    __NO_CONNECTION_TEXT = 'No connection with backend'

    def __init__(self, user_service_host: str, user_service_port: int) -> None:
        base_url: str = f'http://{user_service_host}:{user_service_port}'
        self.__session = aiohttp.ClientSession(base_url=base_url)

    async def terminate(self) -> None:
        """
        Terminates agent and free underlying resources.
        """

        await self.__session.close()

    async def create_user(self, telegram_id: int) -> None:
        url: str = self.__get_users_url(telegram_id)
        try:
            response = await self.__session.post(url=url)
            parsed_response = DefaultResponse.model_validate_json(await response.text())
            self.__validate_add_user_code(parsed_response.status.code)
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def delete_user(self, telegram_id: int) -> None:
        url: str = self.__get_users_url(telegram_id)
        try:
            response = await self.__session.delete(url=url)
            parsed_response = DefaultResponse.model_validate_json(await response.text())
            self.__validate_delete_user(parsed_response.status.code)
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def add_user_track_list(self, telegram_id: int, track_list_url: str) -> Playlist:
        url: str = self.__get_user_track_lists_url(telegram_id)
        try:
            response = await self.__session.post(url=url, params={'url': track_list_url})
            parsed_response = UserTrackListResponse.model_validate_json(await response.text())
            self.__validate_add_link(parsed_response.status.code)
            if parsed_response.track_list is None:
                raise InternalErrorException('No track list when add user track list is successful')
            return parsed_response.track_list
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def delete_user_track_list(self, telegram_id: int, track_list_url: str) -> None:
        url: str = self.__get_user_track_lists_url(telegram_id)
        try:
            response = await self.__session.delete(url=url, params={'url': track_list_url})
            parsed_response = DefaultResponse.model_validate_json(await response.text())
            self.__validate_delete_link(parsed_response.status.code)
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def add_user_city(self, telegram_id: int, city: str) -> None:
        url: str = self.__get_user_cities_url(telegram_id)

        try:
            response = await self.__session.post(url=url, params={'city': city})
            parsed_response = UserAddCityResponse.model_validate_json(await response.text())
            self.__validate_add_city_code(parsed_response.status.code, parsed_response.city)
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def delete_user_city(self, telegram_id: int, city: str) -> None:
        url: str = self.__get_user_cities_url(telegram_id)

        try:
            response = await self.__session.delete(url=url, params={'city': city})
            parsed_response = DefaultResponse.model_validate_json(await response.text())
            self.__validate_delete_user_city_code(parsed_response.status.code)
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def get_user_track_lists(self, telegram_id: int) -> list[Playlist]:
        url: str = self.__get_user_track_lists_url(telegram_id)

        try:
            response = await self.__session.get(url=url)
            parsed_response = UserTrackListsResponse.model_validate_json(await response.text())
            self.__validate_get_links(parsed_response.status.code)
            return parsed_response.track_lists
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def get_user_cities(self, telegram_id: int) -> list[str]:
        url: str = self.__get_user_cities_url(telegram_id)

        try:
            response = await self.__session.get(url=url)
            parsed_response = UserCitiesResponse.model_validate_json(await response.text())
            self.__validate_get_user_cities_code(parsed_response.status.code)
            return parsed_response.cities
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def get_user_concerts(self, telegram_id: int) -> list[Concert]:
        url: str = self.__get_user_concerts_url(telegram_id)

        try:
            response = await self.__session.get(url=url)
            parsed_response = UserConcertsResponse.model_validate_json(await response.text())
            self.__validate_get_concerts(parsed_response.status.code)
            return parsed_response.concerts
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e

    async def add_user_city_by_coordinates(self, telegram_id: int, lat: float, lon: float) -> str:
        url = self.__get_user_cities_url(telegram_id)

        try:
            response = await self.__session.post(url=url, params={'lat': lat, 'lon': lon})
            parsed_response = UserAddCityResponse.model_validate_json(await response.text())
            self.__validate_add_city_by_coordinates(parsed_response.status.code)
            if parsed_response.city is None:
                raise InternalErrorException('No city when add city by coordinates is successful')
            return parsed_response.city
        except ValueError as e:
            raise InternalErrorException(self.__BAD_ANSWER_TEXT) from e
        except ClientConnectionError as e:
            logging.log(level=logging.WARNING, msg=str(e))
            raise InternalErrorException(self.__NO_CONNECTION_TEXT) from e



    @staticmethod
    def __get_users_url(telegram_id: int) -> str:
        return f'/users/{telegram_id}'

    @staticmethod
    def __get_user_cities_url(telegram_id: int) -> str:
        return f'{UserServiceAgentImpl.__get_users_url(telegram_id)}/cities'

    @staticmethod
    def __get_user_track_lists_url(telegram_id: int) -> str:
        return f'{UserServiceAgentImpl.__get_users_url(telegram_id)}/track-lists'

    @staticmethod
    def __get_user_concerts_url(telegram_id: int) -> str:
        return f'{UserServiceAgentImpl.__get_users_url(telegram_id)}/concerts'

    @staticmethod
    def __check_user_not_found(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.USER_NOT_FOUND:
            raise UserDoesNotExistException()

    @staticmethod
    def __check_internal_error(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.INTERNAL_ERROR:
            raise InternalErrorException('Internal error of backend')

    @staticmethod
    def __validate_add_user_code(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_internal_error(status)
        if status == ResponseStatusCode.USER_ALREADY_EXISTS:
            raise UserAlreadyExistsException()

        raise InternalErrorException('Unknown response code on add user')

    @staticmethod
    def __validate_add_city_code(status: ResponseStatusCode, variant: Optional[str]) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_user_not_found(status)
        UserServiceAgentImpl.__check_internal_error(status)

        if status == ResponseStatusCode.CITY_ALREADY_ADDED:
            raise CityAlreadyAddedException()
        if status == ResponseStatusCode.INVALID_CITY:
            raise InvalidCityException()
        if status == ResponseStatusCode.FUZZY_CITY:
            if variant is None:
                raise InternalErrorException('No city variant when status = FUZZY_CITY')
            raise FuzzyCityException(variant)
        raise InternalErrorException('Unknown response code on add city')

    @staticmethod
    def __validate_get_user_cities_code(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_internal_error(status)
        UserServiceAgentImpl.__check_user_not_found(status)
        raise InternalErrorException('Unknown response code on get user cities')

    @staticmethod
    def __validate_delete_user_city_code(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_internal_error(status)
        UserServiceAgentImpl.__check_user_not_found(status)
        if status == ResponseStatusCode.CITY_NOT_ADDED:
            raise CityNotAddedException()
        raise InternalErrorException('Unknown response code on delete user city')

    @staticmethod
    def __validate_add_link(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_internal_error(status)
        UserServiceAgentImpl.__check_user_not_found(status)
        if status == ResponseStatusCode.TRACKS_LIST_ALREADY_ADDED:
            raise TrackListAlreadyAddedException()
        if status == ResponseStatusCode.INVALID_TRACK_LIST:
            raise InvalidTrackListException()
        raise InternalErrorException('Unknown response code on add link')

    @staticmethod
    def __validate_delete_link(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_internal_error(status)
        UserServiceAgentImpl.__check_user_not_found(status)
        if status == ResponseStatusCode.TRACKS_LIST_NOT_ADDED:
            raise TrackListNotAddedException()
        raise InternalErrorException('Unknown response code on delete link')

    @staticmethod
    def __validate_get_links(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_internal_error(status)
        UserServiceAgentImpl.__check_user_not_found(status)

        raise InternalErrorException('Unknown response code on get links')

    @staticmethod
    def __validate_delete_user(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_internal_error(status)
        UserServiceAgentImpl.__check_user_not_found(status)

        raise InternalErrorException('Unknown response code on delete user')

    @staticmethod
    def __validate_get_concerts(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_internal_error(status)
        UserServiceAgentImpl.__check_user_not_found(status)

        raise InternalErrorException('Unknown response code on get concerts')

    @staticmethod
    def __validate_add_city_by_coordinates(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        UserServiceAgentImpl.__check_user_not_found(status)
        UserServiceAgentImpl.__check_internal_error(status)

        if status == ResponseStatusCode.CITY_ALREADY_ADDED:
            raise CityAlreadyAddedException()
        if status == ResponseStatusCode.INVALID_CITY:
            raise InvalidCityException()
        if status == ResponseStatusCode.INVALID_COORDS:
            raise InvalidCoordsException()
        raise InternalErrorException('Unknown response code on add city by coordinates')
