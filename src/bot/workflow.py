import asyncio
import logging
from traceback import format_exc as traceback

from django.forms import model_to_dict

from common.domain.models import ProxyCredentials
from common.http.client import AsyncHttpClient
from common.utils import get_log_extra as extra
from steam.api import SteamApi
from steam.domain.models import SteamCredentials
from steam.models import Account

logger = logging.getLogger(__name__)


class BotWorkflow:
    def __init__(self, bot: Account):
        self._bot = bot
        dict_ = model_to_dict(self._bot)
        self._proxy_creds = ProxyCredentials.parse_str(self._bot.proxy)
        self._steam_creds = SteamCredentials.parse_obj(dict_).with_guard(**dict_)
        self._session = AsyncHttpClient(self._proxy_creds).session
        self._steam_api = SteamApi(self._steam_creds, self._session)

    async def run(self):
        try:
            logger.info('Trying to start bot workflow...', extra=extra(self._bot.login))
            async with self._steam_api as steam:
                logger.info('Bot workflow start successfully', extra=extra(self._bot.login))

                bot_profile = await steam.get_profile(self._bot.steam_id)
                logger.info(f'Bot profile: {bot_profile}', extra=extra(self._bot.login))

                # TODO: Remove in future
                await self.do_something()
        except Exception as ex:
            logger.error(f'Bot workflow not running by error: {ex}', extra=extra(self._bot.login, traceback()))

    async def do_something(self):
        while True:
            await asyncio.sleep(5)
            logger.info(f'Bot {self._bot.login} sleeping...', extra=extra(self._bot.login))
