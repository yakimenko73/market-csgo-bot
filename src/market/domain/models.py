from typing import Any, List, Dict

from pydantic import BaseModel, Field


class MarketCredentials(BaseModel):
    login: str
    api_key: str = Field(alias='market_api_key')


class BaseMarketResponse(BaseModel):
    success: bool

    def __eq__(self, other: Any) -> bool:
        return self.success == other if isinstance(other, bool) else super(BaseMarketResponse, self).__eq__(other)


class MarketItem(BaseModel):
    class ItemExtra(BaseModel):
        percent_success: float = None
        average_time: int = None
        volume: bool = None
        asset: int = None
        float_: float = Field(alias='float', default=None)
        phase: str = None

    id: str
    price: int
    class_id: int = Field(alias='class')
    instance: int
    extra: ItemExtra


class MarketSiteStatus(BaseModel):
    user_token: bool
    trade_check: bool
    site_online: bool
    site_not_ban: bool = Field(alias='site_notmpban')
    steam_web_api_key: bool


class UpdateInventoryResponse(BaseMarketResponse):
    pass


class SetSteamApiKeyResponse(BaseMarketResponse):
    pass


class PingResponse(BaseMarketResponse):
    ping: str = 'pong'


class TestResponse(BaseMarketResponse):
    status: MarketSiteStatus


class MyInventoryResponse(BaseMarketResponse):
    class Item(BaseModel):
        id: str
        class_id: str = Field(alias='classid')
        instance_id: str = Field(alias='instanceid')
        market_hash_name: str
        market_price: float
        tradable: bool

    items: List[Item]


class GetItemsByHashNameResponse(BaseMarketResponse):
    currency: str = None
    data: Dict[str, List[MarketItem]] = None
    error: str = None
