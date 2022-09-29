import logging

from aiohttp import ClientResponse
from django.conf import settings

from common.http.client import AsyncHttpClient
from common.utils import get_log_extra as extra
from market.domain.enums import MarketApi as MarketUrls
from market.domain.models import *

logger = logging.getLogger(__name__)


class MarketApi:
    def __init__(self, creds: MarketCredentials, client: AsyncHttpClient):
        self._creds = creds
        self._api_key = self._creds.api_key
        self._client = client
        self._settings = settings.MARKET_SETTINGS
        self._host = self._settings.host

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

    async def _extra(self, response: ClientResponse) -> dict:
        json = await response.json()
        return extra(self._creds.login, request=str(response.url), response=str(json), status_code=response.status)

    async def _get_api(self, api: MarketUrls, **kwargs) -> ClientResponse:
        return await self._client.get(self._get_uri(api), self._get_params(**kwargs))

    def _get_uri(self, api: MarketUrls) -> str:
        return self._host + api.value

    def _get_params(self, **kwargs) -> dict:
        return dict(key=self._api_key, **kwargs)
