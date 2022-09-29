from abc import ABC
from typing import Any

from aiohttp import ClientSession, ClientResponse
from aiohttp_socks import ProxyConnector

from common.domain.models import ProxyCredentials


class BaseHttpClient(ABC):
    def get(self, uri: str):
        raise NotImplementedError()

    def post(self, uri: str, data: Any):
        raise NotImplementedError()


class AsyncHttpClient(BaseHttpClient):
    def __init__(self, proxy: ProxyCredentials = None):
        self._proxy_connector = None if not proxy else ProxyConnector(**proxy.dict())
        self._session = ClientSession(connector=self._proxy_connector)

    @property
    def session(self) -> ClientSession:
        return self._session

    @session.setter
    def session(self, session: ClientSession):
        self._session = session

    async def get(self, uri, params: dict = None) -> ClientResponse:
        return await self._session.get(uri, params=params)

    async def post(self, uri, data) -> ClientResponse:
        return await self._session.post(uri, data=data)
