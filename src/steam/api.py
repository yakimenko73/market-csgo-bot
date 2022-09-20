import logging

from aiohttp import ClientSession
from asyncsteampy.client import SteamClient
from asyncsteampy.exceptions import InvalidCredentials, CaptchaRequired

from common.utils import get_log_extra as extra
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
        try:
            await self.login()
        except Exception as ex:
            await self._session.close()
            raise ex

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.logout()

    async def login(self):
        try:
            await self._client.login()
            logger.info('Steam login complete', extra=extra(self._bot_name))
        except InvalidCredentials as ex:
            logger.error('Invalid steam credentials', extra=extra(self._bot_name))
            raise ex
        except CaptchaRequired as ex:
            logger.error('Required captcha for steam login', extra=extra(self._bot_name))
            raise ex

    async def logout(self):
        await self._client.close()
        logger.info('Steam logout complete', extra=extra(self._bot_name))

    async def get_profile(self, steam_id: str) -> dict:
        return await self._client.get_profile(steam_id)

    def logged_in(self) -> bool:
        return self._client.was_login_executed
