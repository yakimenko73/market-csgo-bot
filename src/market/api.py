import logging
from typing import Final, Iterable

from aiohttp import ClientResponse
from django.conf import settings

from common.http.client import AsyncHttpClient
from common.utils import get_log_extra as extra
from market.domain.constants import LOG_MAX_LENGTH
from market.domain.enums import MarketUrls
from market.domain.models import *

logger = logging.getLogger(__name__)

API_KEY_QUERY_PARAM: Final[str] = 'key'


class MarketApi:
    def __init__(self, creds: MarketCredentials, client: AsyncHttpClient):
        self._creds = creds
        self._client = client
        self._settings = settings.MARKET_SETTINGS

    async def set_steam_api_key(self, steam_key: str) -> SetSteamApiKeyResponse:
        response = await self._get_api(MarketUrls.SET_STEAM_API_KEY, steam_api_key=steam_key)
        logger.info(f'Set steam api key', extra=await self._extra(response))

        return SetSteamApiKeyResponse(**await response.json())

    async def ping(self) -> PingResponse:
        response = await self._get_api(MarketUrls.PING)
        logger.info('Sent market ping', extra=await self._extra(response))

        return PingResponse(**await response.json())

    async def test(self) -> TestResponse:
        response = await self._get_api(MarketUrls.TEST)
        logger.info('Sent market test', extra=await self._extra(response))

        return TestResponse(**await response.json())

    async def get_inventory(self) -> MyInventoryResponse:
        response = await self._get_api(MarketUrls.GET_INVENTORY)
        logger.info('Get inventory', extra=await self._extra(response))

        return MyInventoryResponse(**await response.json())

    async def update_inventory(self) -> UpdateInventoryResponse:
        response = await self._get_api(MarketUrls.UPDATE_INVENTORY)
        logger.info('Update inventory', extra=await self._extra(response))

        return UpdateInventoryResponse(**await response.json())

    async def get_items_by_hash_name(self, key: str, hash_names: Iterable[str]):
        params = {'key': key, 'list_hash_name[]': hash_names}
        response = await self._get_api(MarketUrls.GET_ITEMS_BY_HASH_NAME, **params)
        logger.info('Get items by hash names', extra=await self._extra(response))

        return GetItemsByHashNameResponse(**await response.json())

    async def _extra(self, response: ClientResponse) -> dict:
        json = await response.json()
        return extra(
            self._creds.login,
            request=str(response.url)[:LOG_MAX_LENGTH],
            response=str(json)[:LOG_MAX_LENGTH],
            status_code=response.status
        )

    async def _get_api(self, api: MarketUrls, **kwargs) -> ClientResponse:
        return await self._client.get(self._get_uri(api), self._get_params(**kwargs))

    def _get_uri(self, api: MarketUrls) -> str:
        return self._settings.host + api.value

    def _get_params(self, **kwargs) -> dict:
        params = dict(**kwargs)
        if API_KEY_QUERY_PARAM not in params:
            params[API_KEY_QUERY_PARAM] = self._creds.api_key
        return params
