from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

from common.domain.models import ProxyCredentials


class AsyncHttpClient:
    def __init__(self, proxy: ProxyCredentials = None):
        self._proxy_connector = None if proxy is None else ProxyConnector(**proxy.dict())
        self._session = ClientSession(connector=self._proxy_connector)

    @property
    def session(self) -> ClientSession:
        return self._session

    @session.setter
    def session(self, session: ClientSession):
        self._session = session
