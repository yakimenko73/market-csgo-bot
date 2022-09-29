from string import Template
from typing import Final, Any, List

from pydantic import BaseModel, Field

MARKET_KEY_QUERY_PARAM: Final[str] = 'key=$key'


class MarketUrls:
    PING: Final[Template] = Template(f'/api/v2/ping?{MARKET_KEY_QUERY_PARAM}')
    TEST: Final[Template] = Template(f'/api/v2/test?{MARKET_KEY_QUERY_PARAM}')
    SET_STEAM_API_KEY: Final[Template] = Template(
        f'/api/v2/set-steam-api-key?{MARKET_KEY_QUERY_PARAM}&steam-api-key=$steam_key'
    )
    GET_INVENTORY: Final[Template] = Template(f'/api/v2/my-inventory?{MARKET_KEY_QUERY_PARAM}')
    UPDATE_INVENTORY: Final[Template] = Template(f'/api/v2/update-inventory?{MARKET_KEY_QUERY_PARAM}')


class MarketCredentials(BaseModel):
    login: str
    api_key: str = Field(alias='market_api_key')


class BaseMarketResponse(BaseModel):
    success: bool

    def __eq__(self, other: Any) -> bool:
        return self.success == other if isinstance(other, bool) else super(BaseMarketResponse, self).__eq__(other)


class MarketItem(BaseModel):
    id: str
    class_id: str = Field(alias='classid')
    instance_id: str = Field(alias='instanceid')
    market_hash_name: str
    market_price: str
    tradable: bool


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
    items: List[MarketItem]
