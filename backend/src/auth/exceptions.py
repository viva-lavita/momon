from fastapi import status

from src.auth import constants
from src.exceptions import HTTPResponseException


class InactiveUserException(HTTPResponseException):
    def __init__(self, status_code=None):
        super().__init__(detail=constants.INACTIVE_USER)


class AuthUnauthorizedException(HTTPResponseException):
    def __init__(self, detail=None, headers=None):
        super().__init__(status.HTTP_401_UNAUTHORIZED, {"WWW-Authenticate": "Bearer"})


class IncorrectUsernameOrPasswordException(AuthUnauthorizedException):
    def __init__(self):
        super().__init__(constants.INCORRECT_USERNAME_OR_PASSWORD)


class NotValidCredentialsException(AuthUnauthorizedException):
    def __init__(self):
        super().__init__(constants.NOT_VALID_CREDENTIALS)


class UserNotFoundException(HTTPResponseException):
    def __init__(self):
        super().__init__(status.HTTP_404_NOT_FOUND, detail=constants.USER_NOT_FOUND)
