import aiohttp

from model import Concert
from ..agent import UserServiceAgent
from ..response import UserTrackListsResponse, UserCitiesResponse, UserConcertsResponse


class UserServiceAgentImpl(UserServiceAgent):
    __session: aiohttp.ClientSession

    def __init__(self, user_service_host: str, user_service_port: int) -> None:
        base_url: str = f'http://{user_service_host}:{user_service_port}/'
        self.__session = aiohttp.ClientSession(base_url=base_url)

    async def terminate(self) -> None:
        """
        Terminates agent and free underlying resources.
        """

        await self.__session.close()

    async def create_user(self, telegram_id: int) -> None:
        url: str = self.__get_users_url(telegram_id)
        await self.__session.post(url=url)

    async def delete_user(self, telegram_id: int) -> None:
        url: str = self.__get_users_url(telegram_id)
        await self.__session.delete(url=url)

    async def add_user_track_list(self, telegram_id: int, track_list_url: str) -> None:
        url: str = self.__get_user_track_lists_url(telegram_id)
        await self.__session.post(url=url, params={'url': track_list_url})

    async def delete_user_track_list(self, telegram_id: int, track_list_url: str) -> None:
        url: str = self.__get_user_track_lists_url(telegram_id)
        await self.__session.delete(url=url, params={'url': track_list_url})

    async def add_user_city(self, telegram_id: int, city: str) -> None:
        url: str = self.__get_user_cities_url(telegram_id)
        await self.__session.post(url=url, params={'city': city})

    async def delete_user_city(self, telegram_id: int, city: str) -> None:
        url: str = self.__get_user_cities_url(telegram_id)
        await self.__session.delete(url=url, params={'city': city})

    async def get_user_track_lists(self, telegram_id: int) -> list[str]:
        url: str = self.__get_user_track_lists_url(telegram_id)

        async with self.__session.get(url=url) as response:
            return UserTrackListsResponse.model_validate_json(await response.text()).track_lists

    async def get_user_cities(self, telegram_id: int) -> list[str]:
        url: str = self.__get_user_cities_url(telegram_id)

        async with self.__session.get(url=url) as response:
            return UserCitiesResponse.model_validate_json(await response.text()).cities

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
