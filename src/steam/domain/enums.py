from typing import Tuple, Any

from common.utils import BaseEnum


class Status(BaseEnum):
    New = 65536
    NotAtSteamInv = 131072
    Check = 262144
    Wait = 51
    Offered = 1001

    @staticmethod
    def get_market_statuses() -> Tuple[Any, Any]:
        return Status.Wait.value, Status.Offered.value,


class HoldStatus(BaseEnum):
    Undefined = 67108864
    Hold = 33554432
    NotAtHold = 16777216


class Place(BaseEnum):
    Google885 = 1
    Google886 = 2
    Google888 = 16
    Casino = 5
    Unknown = 8


class CorrectName(BaseEnum):
    Yes = 256
    No = 512
    Wait = 1024
