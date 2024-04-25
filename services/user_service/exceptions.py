from datetime import datetime


class UserServiceException(Exception):
    pass


class InternalErrorException(UserServiceException):
    pass


class UserAlreadyExistsException(UserServiceException):
    def __init__(self, date: datetime):
        self.date = date
        super().__init__()


class UserDoesNotExistException(UserServiceException):
    pass


class CityAlreadyAddedException(UserServiceException):
    pass


class CityNotAddedException(UserServiceException):
    pass


class InvalidCityException(UserServiceException):
    pass


class FuzzyCityException(UserServiceException):
    def __init__(self, variant: str | None):
        self.variant = variant
        super().__init__()
    pass


class TrackListAlreadyAddedException(UserServiceException):
    pass


class TrackListNotAddedException(UserServiceException):
    pass


class InvalidTrackListException(UserServiceException):
    pass
