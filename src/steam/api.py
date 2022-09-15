import logging

from aiohttp import ClientSession
from asyncsteampy.client import SteamClient

from .domain.models import SteamCredentials

logger = logging.getLogger(__name__)


class SteamApi:
    def __init__(self, steam_creds: SteamCredentials, session: ClientSession):
        self._bot_name = steam_creds.login
        self._session = session
        self._client = SteamClient(
            steam_creds.login,
            steam_creds.password,
            steam_guard=steam_creds.guard.dict(by_alias=False),
            api_key=steam_creds.api_key,
            session=self._session
        )

    async def __aenter__(self):
        await self._client.login()
        logger.info('Steam login complete', extra={'account': self._bot_name})

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.close()
        logger.info('Steam logout complete', extra={'account': self._bot_name})

    async def get_profile(self, steam_id: str) -> dict:
        return await self._client.get_profile(steam_id)

    def logged_in(self) -> bool:
        return self._client.was_login_executed
