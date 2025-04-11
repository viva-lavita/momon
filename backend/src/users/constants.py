from enum import Enum


class UserRolesEnum(str, Enum):
    admin = "admin"
    user = "user"


INACTIVE_USER = "Inactive user"
