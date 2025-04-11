from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTBearer(OAuth2PasswordBearer):
    def __init__(self, *args, **kwargs):
        kwargs["scheme_name"] = "JWT"
        kwargs["description"] = "TODO: Дописать описание"
        super(JWTBearer, self).__init__(*args, **kwargs)


INCORRECT_USERNAME_OR_PASSWORD = (
    "Incorrect username or password, user not found."  # pragma: allowlist secret
)
NOT_VALID_CREDENTIALS = "Could not validate credentials"
