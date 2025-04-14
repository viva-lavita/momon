from fastapi import status


class CRUDError(Exception):
    pass


class ObjectNotFoundError(CRUDError):
    pass


class HTTPResponseException(Exception):
    """
    Base class for all HTTP exceptions.
    """

    def __init__(self, status_code=None, headers=None, detail=None):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

    def dict(self):
        return {
            "status_code": self.status_code,
            "detail": self.detail,
            "headers": self.headers,
        }


class EmailsDisabledException(HTTPResponseException):
    def __init__(self, detail=None, headers=None):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
