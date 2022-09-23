import threading
from enum import Enum
from typing import Any, List, Tuple

from envclasses import load_env


class BaseSettings:
    @classmethod
    def from_env(cls, prefix: str) -> Any:
        load_env(instance := cls(), prefix)
        return instance


class BaseEnum(Enum):
    @classmethod
    def to_list(cls) -> List[Tuple[int, str]]:
        return [(member.value, member.name) for member in cls]


def use_thread(func):
    def inner_function(*args, **kwargs):
        return func(*args, **kwargs)

    threading.Thread(target=inner_function, daemon=True).start()


# TODO: Refactor
def get_log_extra(
        account: str = None,
        traceback: str = None,
        request: str = None,
        response: str = None,
        status_code: int = None,
) -> dict:
    extra = {}
    if account:
        extra['account'] = account
    if traceback:
        extra['traceback'] = traceback
    if request:
        extra['request'] = request
    if response:
        extra['response'] = response
    if status_code:
        extra['status_code'] = status_code

    return extra
