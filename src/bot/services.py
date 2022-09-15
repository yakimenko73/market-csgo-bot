import asyncio
import logging
from typing import List

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from django.forms import model_to_dict
from steam.api import SteamApi
from steam.domain.models import SteamCredentials, ProxyCredentials
from steam.models import Account

logger = logging.getLogger(__name__)


class BotService:
    def __init__(self, bot_account: Account):
        self._bot = bot_account
        dict_ = model_to_dict(self._bot)
        self._proxy_creds = ProxyCredentials.parse_str(self._bot.proxy)
        self._steam_creds = SteamCredentials.parse_obj(dict_).with_guard(**dict_)
        self._session = ClientSession(connector=ProxyConnector(**self._proxy_creds.dict()))
        self._steam_api = SteamApi(self._steam_creds, self._session)

    async def run_workflow(self):
        async with self._steam_api as steam:
            logger.info('Bot workflow start successfully', extra={'account': self._bot.login})
            bot_profile = await steam.get_profile(self._bot.steam_id)
            logger.info(f'Bot profile: {bot_profile}', extra={'account': self._bot.login})

    @classmethod
    async def run_bots(cls, bots: List[Account]):
        tasks = []
        for bot in bots:
            instance = cls(bot)
            tasks.append(asyncio.create_task(instance.run_workflow()))

        [await task for task in tasks]
