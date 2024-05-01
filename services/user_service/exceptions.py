class UserServiceException(Exception):
    pass


class InternalErrorException(UserServiceException):
    pass


class UserAlreadyExistsException(UserServiceException):
    pass


class UserDoesNotExistException(UserServiceException):
    pass


class CityAlreadyAddedException(UserServiceException):
    pass


class CityNotAddedException(UserServiceException):
    pass


class InvalidCityException(UserServiceException):
    pass


class FuzzyCityException(UserServiceException):
    __variant: str

    def __init__(self, variant: str):
        self.__variant = variant
        super().__init__()

    @property
    def variant(self) -> str:
        return self.__variant


class TrackListAlreadyAddedException(UserServiceException):
    pass


class TrackListNotAddedException(UserServiceException):
    pass


class InvalidTrackListException(UserServiceException):
    pass
