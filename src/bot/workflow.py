import asyncio
import logging
from traceback import format_exc as traceback

from django.forms import model_to_dict

from common.domain.models import ProxyCredentials
from common.http.client import AsyncHttpClient
from common.utils import get_log_extra as extra
from market.api import MarketApi
from market.domain.models import MarketCredentials
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
        self._market_creds = MarketCredentials.parse_obj(dict_)

        self._http_client = AsyncHttpClient(self._proxy_creds)
        self._steam_api = SteamApi(self._steam_creds, self._http_client.session)
        self._market_api = MarketApi(self._market_creds, self._http_client)

    async def run(self):
        try:
            logger.info('Trying to start bot workflow...', extra=extra(self._bot.login))
            async with self._steam_api as steam:
                logger.info('Bot workflow start successfully', extra=extra(self._bot.login))

                await self._market_api.set_steam_api_key(self._bot.steam_api)
                await self._market_api.ping()
                await self._market_api.test()

                await self.work_simulation()
        except Exception as ex:
            logger.error(f'Bot workflow not running by error: {ex}', extra=extra(self._bot.login, traceback()))

    async def work_simulation(self):
        while True:
            await asyncio.sleep(5)
            logger.info(f'Bot sleeping...', extra=extra(self._bot.login))
