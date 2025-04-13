from fastapi import status

from src.exceptions import HTTPResponseException


class UserAlreadyExists(Exception):
    pass


class UserNotFound(Exception):
    pass


class UserAlreadyExistsException(HTTPResponseException):
    def __init__(self):
        super().__init__(
            detail="User already exists", status_code=status.HTTP_400_BAD_REQUEST
        )
