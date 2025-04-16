from enum import Enum


class UserRolesEnum(str, Enum):
    admin = "admin"
    user = "user"


INACTIVE_USER = "Inactive user"
PASSWORD_UPDATED_SUCCESSFULLY = "Password updated successfully"  # pragma: allowlist secret
USER_DELETED_SUCCESSFULLY = "User deleted successfully"
USER_ALREADY_EXISTS = "User with this email or username already exists"
INVALID_PASSWORD = "Invalid password"  # pragma: allowlist secret
INCORRECT_PASSWORD = "New password cannot be the same as the current one"
CANNOT_DELETE_SUPERUSER = "Super users are not allowed to delete themselves"
ROLE_NOT_FOUND = "Role not found"
