from fastapi import status

from src.auth import constants
from src.exceptions import HTTPResponseException


class AuthForbiddenException(HTTPResponseException):
    def __init__(self, headers=None, detail=None):
        super().__init__(status.HTTP_403_FORBIDDEN)


class InactiveUserException(AuthForbiddenException):
    def __init__(self):
        super().__init__(detail=constants.INACTIVE_USER)


class AuthUnauthorizedException(HTTPResponseException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, {"WWW-Authenticate": "Bearer"})


class IncorrectUsernameOrPasswordException(AuthUnauthorizedException):
    def __init__(self):
        super().__init__(constants.INCORRECT_USERNAME_OR_PASSWORD)


class NotValidCredentialsException(AuthUnauthorizedException):
    def __init__(self):
        super().__init__(constants.NOT_VALID_CREDENTIALS)
