class CRUDError(Exception):
    pass


class ObjectNotFoundError(CRUDError):
    pass


class HTTPResponseException(Exception):
    def __init__(self, status_code, headers, detail):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

    def dict(self):
        return {
            "status_code": self.status_code,
            "detail": self.detail,
            "headers": self.headers,
        }
