from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel

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
    asset_id: str
    trade_id: str
    drive_discount: str
    drive_discount_percent: str
    correct_name: CorrectName

    class Config:
        use_enum_values = True

    def to_dict(self) -> dict:
        exclude_fields = {'owner_bot', 'bot', 'ru_name'}
        if self.status == Status.New.value:
            exclude_fields.add('status')

        dict_ = self.dict(exclude=exclude_fields)
        dict_['market_ru_name'] = self.ru_name
        return dict_

    def get_names(self):
        dict_ = self.to_dict()
        dict_.pop('asset_id')
        return list(dict_.keys())


class ItemsJsonModel(BaseModel):
    items: List[dict]
    # currency rate
    u: float
