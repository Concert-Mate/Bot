from datetime import datetime

import aiohttp
from aiohttp import ClientConnectionError

from model import Concert
from .. import InternalErrorException, UserAlreadyExistsException, TrackListNotAddedException, \
    CityAlreadyAddedException, UserDoesNotExistException, InvalidCityException, FuzzyCityException, \
    CityNotAddedException, TrackListAlreadyAddedException, InvalidTrackListException
from ..agent import UserServiceAgent
from ..response import UserTrackListsResponse, UserCitiesResponse, UserConcertsResponse, DefaultResponse, \
    ResponseStatusCode
from ..response.user_add_city_response import UserAddCityResponse


class UserServiceAgentImpl(UserServiceAgent):
    __session: aiohttp.ClientSession

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
            try:
                parsed_response = DefaultResponse.model_validate_json(await response.text())
                self.__validate_add_user_code(parsed_response.status.code)
            except ValueError as e:
                raise InternalErrorException('BAD ANSWER') from e
        except ClientConnectionError as e:
            print(e)
            raise InternalErrorException('NO CONNECTION')

    async def delete_user(self, telegram_id: int) -> None:
        url: str = self.__get_users_url(telegram_id)
        await self.__session.delete(url=url)

    async def add_user_track_list(self, telegram_id: int, track_list_url: str) -> None:
        url: str = self.__get_user_track_lists_url(telegram_id)
        try:
            response = await self.__session.post(url=url, params={'url': track_list_url})
            try:
                parsed_response = DefaultResponse.model_validate_json(await response.text())
                self.__validate_add_link(parsed_response.status.code)
            except ValueError as e:
                raise InternalErrorException('BAD ANSWER') from e
        except ClientConnectionError as e:
            print(e)
            raise InternalErrorException('NO CONNECTION')


    async def delete_user_track_list(self, telegram_id: int, track_list_url: str) -> None:
        url: str = self.__get_user_track_lists_url(telegram_id)
        try:
            response = await self.__session.delete(url=url, params={'url': track_list_url})
            try:
                parsed_response = DefaultResponse.model_validate_json(await response.text())
                self.__validate_delete_link(parsed_response.status.code)
            except ValueError as e:
                raise InternalErrorException('BAD ANSWER') from e
        except ClientConnectionError as e:
            print(e)
            raise InternalErrorException('NO CONNECTION')


    async def add_user_city(self, telegram_id: int, city: str) -> None:
        url: str = self.__get_user_cities_url(telegram_id)

        try:
            response = await self.__session.post(url=url, params={'city': city})
            try:
                parsed_response = UserAddCityResponse.model_validate_json(await response.text())
                self.__validate_add_city_code(parsed_response.status.code, parsed_response.variant)
            except ValueError as e:
                raise InternalErrorException('BAD ANSWER') from e
        except ClientConnectionError as e:
            print(e)
            raise InternalErrorException('NO CONNECTION')

    async def delete_user_city(self, telegram_id: int, city: str) -> None:
        url: str = self.__get_user_cities_url(telegram_id)

        try:
            response = await self.__session.delete(url=url, params={'city': city})
            try:
                parsed_response = DefaultResponse.model_validate_json(await response.text())
                self.__validate_delete_user_city_code(parsed_response.status.code)
            except ValueError as e:
                raise InternalErrorException('BAD ANSWER') from e
        except ClientConnectionError as e:
            print(e)
            raise InternalErrorException('NO CONNECTION')


    async def get_user_track_lists(self, telegram_id: int) -> list[str]:
        url: str = self.__get_user_track_lists_url(telegram_id)

        try:
            response = await self.__session.get(url=url)
            try:
                text = await response.text()
                print(text)
                parsed_response = UserTrackListsResponse.model_validate_json(await response.text())
                self.__validate_get_links(parsed_response.status.code)
                return parsed_response.track_lists
            except ValueError as e:
                raise InternalErrorException('BAD ANSWER') from e
        except ClientConnectionError as e:
            print(e)
            raise InternalErrorException('NO CONNECTION')

    async def get_user_cities(self, telegram_id: int) -> list[str]:
        url: str = self.__get_user_cities_url(telegram_id)

        try:
            response = await self.__session.get(url=url)
            try:
                parsed_response = UserCitiesResponse.model_validate_json(await response.text())
                self.__validate_get_user_cities_code(parsed_response.status.code)
                return parsed_response.cities
            except ValueError as e:
                raise InternalErrorException('BAD ANSWER') from e
        except ClientConnectionError as e:
            print(e)
            raise InternalErrorException('NO CONNECTION')

    async def get_user_concerts(self, telegram_id: int) -> list[Concert]:
        url: str = self.__get_user_concerts_url(telegram_id)

        async with self.__session.get(url=url) as response:
            return UserConcertsResponse.model_validate_json(await response.text()).concerts

    @staticmethod
    def __get_users_url(telegram_id: int) -> str:
        return f'/users/{telegram_id}'

    @staticmethod
    def __get_user_cities_url(telegram_id: int) -> str:
        return f'{UserServiceAgentImpl.__get_users_url(telegram_id)}/cities'

    @staticmethod
    def __get_user_track_lists_url(telegram_id: int) -> str:
        return f'{UserServiceAgentImpl.__get_users_url(telegram_id)}/tracks-lists'

    @staticmethod
    def __get_user_concerts_url(telegram_id: int) -> str:
        return f'{UserServiceAgentImpl.__get_users_url(telegram_id)}/concerts'

    @staticmethod
    def __validate_add_user_code(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        if status == ResponseStatusCode.USER_ALREADY_EXISTS:
            raise UserAlreadyExistsException(date=datetime.now())

        raise InternalErrorException("Unknown response code on add user")

    @staticmethod
    def __validate_add_city_code(status: ResponseStatusCode, variants: str | None) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        if status == ResponseStatusCode.CITY_ALREADY_ADDED:
            raise CityAlreadyAddedException()
        if status == ResponseStatusCode.USER_NOT_FOUND:
            raise UserDoesNotExistException()
        if status == ResponseStatusCode.INVALID_CITY:
            raise InvalidCityException()
        if status == ResponseStatusCode.FUZZY_CITY:
            raise FuzzyCityException(variants)
        raise InternalErrorException("Unknown response code on add city")

    @staticmethod
    def __validate_get_user_cities_code(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        if status == ResponseStatusCode.USER_NOT_FOUND:
            raise UserDoesNotExistException()
        raise InternalErrorException("Unknown response code on get user cities")

    @staticmethod
    def __validate_delete_user_city_code(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        if status == ResponseStatusCode.USER_NOT_FOUND:
            raise UserDoesNotExistException()
        if status == ResponseStatusCode.CITY_NOT_ADDED:
            raise CityNotAddedException()
        raise InternalErrorException("Unknown response code on remove user city")

    @staticmethod
    def __validate_add_link(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        if status == ResponseStatusCode.TRACKS_LIST_ALREADY_ADDED:
            raise TrackListAlreadyAddedException()
        if status == ResponseStatusCode.INVALID_TRACK_LIST:
            raise InvalidTrackListException()
        if status == ResponseStatusCode.USER_NOT_FOUND:
            raise UserDoesNotExistException()
        raise InternalErrorException("Unknown response code on add link")

    @staticmethod
    def __validate_delete_link(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        if status == ResponseStatusCode.TRACKS_LIST_NOT_ADDED:
            raise TrackListNotAddedException()
        if status == ResponseStatusCode.USER_NOT_FOUND:
            raise UserDoesNotExistException()
        raise InternalErrorException("Unknown response code on delete link")

    @staticmethod
    def __validate_get_links(status: ResponseStatusCode) -> None:
        if status == ResponseStatusCode.SUCCESS:
            return
        if status == ResponseStatusCode.USER_NOT_FOUND:
            raise UserDoesNotExistException()
        raise InternalErrorException("Unknown response code on get lins")
