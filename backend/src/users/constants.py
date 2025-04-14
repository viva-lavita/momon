from enum import Enum


class UserRolesEnum(str, Enum):
    admin = "admin"
    user = "user"


INACTIVE_USER = "Inactive user"
PASSWORD_UPDATED_SUCCESSFULLY = (
    "Password updated successfully"  # pragma: allowlist secret
)
