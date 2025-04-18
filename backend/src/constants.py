import os
from enum import Enum
from pathlib import Path
from uuid import uuid4


class Environment(str, Enum):
    LOCAL = "LOCAL"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self) -> bool:
        return self in (self.LOCAL, self.STAGING, self.TESTING)

    @property
    def is_testing(self) -> bool:
        return self == self.TESTING

    @property
    def is_deployed(self) -> bool:
        return self not in (self.TESTING)

    @property
    def is_local(self) -> bool:
        return self == self.LOCAL


def new_uuid() -> str:
    return str(uuid4())


def get_base_dir() -> str:
    return os.path.dirname(__file__)


def get_project_root() -> str:
    return Path(__file__).resolve().parent.parent


EMAILS_DISABLED = "Emails are disabled"
