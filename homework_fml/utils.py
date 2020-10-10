from enum import Enum, auto


class ErrorReason(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __str__(self):
        return self.name

    EXCEPTION = auto()
    EMAIL_ALREADY_REGISTERED = auto()
    PASSWORD_TOO_SHORT = auto()
    PASSWORDS_DIFFER = auto()
    WRONG_LOGIN = auto()
    ACCOUNT_NOT_ACTIVE = auto()
    TOKEN_EXPIRED = auto()
    TOKEN_INVALID = auto()
    DUE_IN_PAST = auto()
    UNAUTHORIZED = auto()
