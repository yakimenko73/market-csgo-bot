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


def get_socks5_string(raw_proxy: str) -> str:
    ip, port, user, password = raw_proxy.split(':')

    return f'socks5://{user}:{password}@{ip}:{port}'
