from string import Template
from typing import Final

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
