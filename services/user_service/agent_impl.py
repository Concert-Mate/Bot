from model import Concert
from .agent import UserServiceAgent


class UserServiceAgentImpl(UserServiceAgent):
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
