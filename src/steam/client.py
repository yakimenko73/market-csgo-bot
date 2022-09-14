from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from asyncsteampy.client import SteamClient as AsyncSteamClient

from .domain.models import SteamCredentials, ProxyCredentials, SteamGuard


class SteamClient:
    def __init__(self, steam_creds: SteamCredentials, steam_guard: SteamGuard, proxy_creds: ProxyCredentials):
        self._connector = ProxyConnector(*list(proxy_creds))
        self._session = ClientSession(connector=self._connector)
        self._client = AsyncSteamClient(
            steam_creds.login,
            steam_creds.password,
            steam_guard=steam_guard.dict(by_alias=False),
            api_key=steam_creds.api_key,
            session=self._session
        )

    async def login(self):
        await self._client.login()
        await self._client.close()
