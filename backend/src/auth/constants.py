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
USER_NOT_FOUND = "The user with this email does not exist in the system."
PASSWORD_RECOVERY_EMAIL_SENT = (
    "Password recovery email sent"  # pragma: allowlist secret
)
INVALID_TOKEN = "Invalid token"
PASSWORD_UPDATED_SUCCESSFULLY = (
    "Password updated successfully"  # pragma: allowlist secret
)
