import logging

from aiohttp import ClientResponse
from django.conf import settings

from common.http.client import AsyncHttpClient
from common.utils import get_log_extra as extra
from market.domain.models import MarketUrls, MarketCredentials, UpdateInventoryResponse, MyInventoryResponse, \
    SetSteamApiKeyResponse, PingResponse, TestResponse

logger = logging.getLogger(__name__)


class MarketApi:
    def __init__(self, creds: MarketCredentials, client: AsyncHttpClient):
        self._creds = creds
        self._api_key = self._creds.api_key
        self._client = client
        self._settings = settings.MARKET_SETTINGS
        self._host = self._settings.host

    async def set_steam_api_key(self, steam_key: str) -> SetSteamApiKeyResponse:
        uri = self._host + MarketUrls.SET_STEAM_API_KEY.substitute(key=self._api_key, steam_key=steam_key)
        response = await self._client.get(uri)
        logger.info(f'Set steam api key', extra=await self._extra(response))

        return SetSteamApiKeyResponse(**await response.json())

    async def ping(self) -> PingResponse:
        uri = self._host + MarketUrls.PING.substitute(key=self._api_key)
        response = await self._client.get(uri)
        logger.info('Sent market ping', extra=await self._extra(response))

        return PingResponse(**await response.json())

    async def test(self) -> TestResponse:
        uri = self._host + MarketUrls.TEST.substitute(key=self._api_key)
        response = await self._client.get(uri)
        logger.info('Sent market test', extra=await self._extra(response))

        return TestResponse(**await response.json())

    async def get_inventory(self) -> MyInventoryResponse:
        uri = self._host + MarketUrls.GET_INVENTORY.substitute(key=self._api_key)
        response = await self._client.get(uri)
        logger.info('Get inventory', extra=await self._extra(response))

        return MyInventoryResponse(**await response.json())

    async def update_inventory(self) -> UpdateInventoryResponse:
        uri = self._host + MarketUrls.UPDATE_INVENTORY.substitute(key=self._api_key)
        response = await self._client.get(uri)
        logger.info('Update inventory', extra=await self._extra(response))

        return UpdateInventoryResponse(**await response.json())

    async def _extra(self, response: ClientResponse) -> dict:
        json = await response.json()
        return extra(self._creds.login, request=str(response.url), response=str(json), status_code=response.status)
