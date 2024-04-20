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
    pass


class TrackListAlreadyAddedException(UserServiceException):
    pass


class TrackListNotAddedException(UserServiceException):
    pass


class InvalidTrackListException(UserServiceException):
    pass
