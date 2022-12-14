from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from .enums import HoldStatus, Status, Place, CorrectName


class ItemModel(BaseModel):
    owner_bot: str
    bot: str
    market_hash_name: str
    ru_name: str
    google_price_usd: float
    google_drive_time: datetime
    steam_price_usd: Decimal
    steam_time: datetime
    hold: datetime
    hold_status: HoldStatus
    status: Status
    place: Place
    asset_id: str = Field(min_length=1)
    trade_id: str
    drive_discount: str
    drive_discount_percent: str
    correct_name: CorrectName

    class Config:
        use_enum_values = True

    def to_dict(self) -> dict:
        exclude_fields = {'owner_bot', 'bot', 'ru_name', 'asset_id'}
        if self.status == Status.Check.value:
            exclude_fields.add('status')

        dict_ = self.dict(exclude=exclude_fields)
        dict_['market_ru_name'] = self.ru_name
        return dict_


class ItemsJsonModel(BaseModel):
    items: List[dict]
    # currency rate
    u: float


class SteamGuard(BaseModel):
    steamid: str = Field(alias='steam_id')
    shared_secret: str
    identity_secret: str


class SteamCredentials(BaseModel):
    login: str
    password: str
    api_key: str = Field(alias='steam_api')
    guard: SteamGuard = None

    def with_guard(self, **kwargs):
        self.guard = SteamGuard.parse_obj(kwargs)

        return self
