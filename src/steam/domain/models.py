from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from .enums import HoldStatus, Status, Place, CorrectName


class ItemModel(BaseModel):
    id: int = None
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
        dict_ = self.dict(exclude={'owner_bot', 'bot', 'ru_name'})
        dict_['market_ru_name'] = self.ru_name
        return dict_
