import logging

from django.conf import settings

from common.http.client import BaseHttpClient
from common.utils import get_log_extra as extra
from market.domain.models import MarketUrls, MarketCredentials

logger = logging.getLogger(__name__)


class MarketApi:
    def __init__(self, creds: MarketCredentials, client: BaseHttpClient):
        self._creds = creds
        self._api_key = self._creds.api_key
        self._client = client
        self._settings = settings.MARKET_SETTINGS
        self._host = self._settings.host

    async def set_steam_api_key(self, steam_key: str):
        path = MarketUrls.SET_STEAM_API_KEY.substitute(key=self._api_key, steam_key=steam_key)

        resp = await self._client.get(self._host + path)
        logger.info(f'Set steam api key. Response: {resp}', extra=extra(self._creds.login, request=path))

    async def ping(self):
        path = MarketUrls.PING.substitute(key=self._api_key)

        resp = await self._client.get(self._host + path)
        logger.info(f'Sent market ping. Response: {resp}', extra=extra(self._creds.login, request=path))

    async def test(self):
        path = MarketUrls.TEST.substitute(key=self._api_key)

        resp = await self._client.get(self._host + path)
        logger.info(f'Sent market test. Response: {resp}', extra=extra(self._creds.login, request=path))
