from enum import Enum, auto
from typing import Union

from flask import jsonify


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
    SPECIFIED = (
        auto()
    )  # use when the error is described in the key error_info (to be shown to the user)


def fail(reason: Union[ErrorReason, str]):
    if type(reason) == str:
        return jsonify(
            {"ok": False, "reason": ErrorReason.SPECIFIED, "error_info": reason}
        )
    return jsonify({"ok": False, "reason": reason})
