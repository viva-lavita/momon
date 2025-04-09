from typing import Annotated
from passlib.context import CryptContext
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTBearer(OAuth2PasswordBearer):
    def __init__(self, *args, **kwargs):
        kwargs["scheme_name"] = "JWT"
        kwargs["description"] = "TODO: Дописать описание"
        super(JWTBearer, self).__init__(*args, **kwargs)

    async def __call__(self, request):
        return await super(JWTBearer, self).__call__(request)


oauth2_scheme = JWTBearer(tokenUrl="login/access-token")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


class NotValidCredentials(Exception):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate credentials"
    headers = {"WWW-Authenticate": "Bearer"}
