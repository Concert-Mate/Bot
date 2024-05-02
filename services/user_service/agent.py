from abc import ABC, abstractmethod

from model import Concert
from model.playlist import Playlist


class UserServiceAgent(ABC):
    @abstractmethod
    async def create_user(self, telegram_id: int) -> None:
        """
        Registers new user.

        :param telegram_id: id of the telegram user
        :raises InternalErrorException: internal error occurred
        :raises UserAlreadyExistsException: user is already registered
        """

    @abstractmethod
    async def delete_user(self, telegram_id: int) -> None:
        """
        Deletes user.

        :param telegram_id: id of the telegram user
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        """

    @abstractmethod
    async def add_user_track_list(self, telegram_id: int, track_list_url: str) -> Playlist:
        """
        Adds tracks list to user.

        :param telegram_id: id of the telegram user
        :param track_list_url: url of track list
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        :raises InvalidTrackListException: url of track list isn't valid
        :raises TrackListAlreadyAddedException: track list is already added
        """

    @abstractmethod
    async def delete_user_track_list(self, telegram_id: int, track_list_url: str) -> None:
        """
        Deletes track list from user.

        :param telegram_id: id of the telegram user
        :param track_list_url: url of track list
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        :raises TrackListNotAddedException: track list is not added to this user
        """

    @abstractmethod
    async def add_user_city(self, telegram_id: int, city: str) -> None:
        """
        Adds city to user.

        :param telegram_id: id of the telegram user
        :param city: city name
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        :raises InvalidCityException: city is invalid
        :raises FuzzyCityException: city is fuzzy (possible variants contain in raised exception)
        :raises CityAlreadyAddedException: city is already added
        """

    @abstractmethod
    async def delete_user_city(self, telegram_id: int, city: str) -> None:
        """
        Deletes city from user.

        :param telegram_id: id of the telegram user
        :param city: city name
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        :raises CityNotAddedException: city is not added to this user
        """

    @abstractmethod
    async def get_user_track_lists(self, telegram_id: int) -> list[Playlist]:
        """
        Returns list of user track lists.

        :param telegram_id: id of the telegram user
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        """

    @abstractmethod
    async def get_user_cities(self, telegram_id: int) -> list[str]:
        """
        Returns list of user cities.

        :param telegram_id: id of the telegram user
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        """

    @abstractmethod
    async def get_user_concerts(self, telegram_id: int) -> list[Concert]:
        """
        Returns list of actual concerts for user.

        :param telegram_id: id of the telegram user
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        """

    @abstractmethod
    async def add_user_city_by_coordinates(self, telegram_id: int, lat: float, lon: float) -> str:
        """
        Add city to user by coordinates
        :param telegram_id: id of telegram user
        :param lat: latitude
        :param lon: longitude
        :raises InternalErrorException: internal error occurred
        :raises UserDoesNotExistException: user isn't registered
        :raises InvalidCityException: no cities by coordinates
        :raises CityAlreadyAddedException: city is already added
        :raise InvalidCoordsException: bad values of coordinates
        """