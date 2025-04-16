from fastapi import status

from src.exceptions import HTTPResponseException
from src.users import constants


class UserAlreadyExists(Exception):
    pass


class UserNotFound(Exception):
    pass


class RoleNotFound(Exception):
    pass


class UserAlreadyExistsException(HTTPResponseException):
    def __init__(self):
        super().__init__(
            detail=constants.USER_ALREADY_EXISTS,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidPasswordException(HTTPResponseException):
    def __init__(self):
        super().__init__(detail=constants.INVALID_PASSWORD, status_code=status.HTTP_400_BAD_REQUEST)


class IncorrectPasswordException(HTTPResponseException):
    def __init__(self):
        super().__init__(
            detail=constants.INCORRECT_PASSWORD,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class SuperuserDeleteException(HTTPResponseException):
    def __init__(self):
        super().__init__(
            detail=constants.CANNOT_DELETE_SUPERUSER,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class RoleNotFoundException(HTTPResponseException):
    def __init__(self):
        super().__init__(detail=constants.ROLE_NOT_FOUND, status_code=status.HTTP_400_BAD_REQUEST)
