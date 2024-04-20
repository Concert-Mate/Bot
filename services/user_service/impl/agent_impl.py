import aiohttp

from model import Concert
from services.user_service.agent import UserServiceAgent


class UserServiceAgentImpl(UserServiceAgent):
    __session: aiohttp.ClientSession

    def __init__(self, user_service_host: str, user_service_port: int) -> None:
        base_url: str = f'http://{user_service_host}:{user_service_port}/'
        self.__session = aiohttp.ClientSession(base_url=base_url)

    async def terminate(self) -> None:
        await self.__session.close()

    async def create_user(self, telegram_id: int) -> None:
        pass

    async def delete_user(self, telegram_id: int) -> None:
        pass

    async def add_user_track_list(self, telegram_id: int, track_list_url: str) -> None:
        pass

    async def delete_user_track_list(self, telegram_id: int, track_list_url: str) -> None:
        pass

    async def add_user_city(self, telegram_id: int, city: str) -> None:
        pass

    async def delete_user_city(self, telegram_id: int, city: str) -> None:
        pass

    async def get_user_track_lists(self, telegram_id: int) -> list[str]:
        pass

    async def get_user_cities(self, telegram_id: int) -> list[str]:
        pass

    async def get_user_concerts(self, telegram_id: int) -> list[Concert]:
        pass
