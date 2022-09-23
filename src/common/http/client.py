from abc import ABC
from typing import Any

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

from common.domain.models import ProxyCredentials


class BaseHttpClient(ABC):
    def get(self, uri):
        raise NotImplementedError()

    def post(self, uri: str, data: Any):
        raise NotImplementedError()


class AsyncHttpClient(BaseHttpClient):
    def __init__(self, proxy: ProxyCredentials = None):
        self._proxy_connector = None if proxy is None else ProxyConnector(**proxy.dict())
        self._session = ClientSession(connector=self._proxy_connector)

    @property
    def session(self) -> ClientSession:
        return self._session

    @session.setter
    def session(self, session: ClientSession):
        self._session = session

    async def get(self, uri) -> dict:
        response = await self._session.get(uri)

        return await response.json()

    async def post(self, uri, data: Any) -> dict:
        response = await self._session.post(uri, data=data)
        return await response.json()
