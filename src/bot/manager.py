import asyncio
import logging
from asyncio import Task
from typing import List, Dict

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from django.forms import model_to_dict
from steam.api import SteamApi
from steam.domain.models import SteamCredentials, ProxyCredentials
from steam.models import Account

logger = logging.getLogger(__name__)


class BotWorkflow:
    def __init__(self, bot: Account):
        self._bot = bot
        dict_ = model_to_dict(self._bot)
        self._proxy_creds = ProxyCredentials.parse_str(self._bot.proxy)
        self._steam_creds = SteamCredentials.parse_obj(dict_).with_guard(**dict_)
        self._session = ClientSession(connector=ProxyConnector(**self._proxy_creds.dict()))
        self._steam_api = SteamApi(self._steam_creds, self._session)

    async def run(self):
        logger.info('Trying to start bot workflow...', self._get_log_extra_data())
        async with self._steam_api as steam:
            logger.info('Bot workflow start successfully', self._get_log_extra_data())

            bot_profile = await steam.get_profile(self._bot.steam_id)
            logger.info(f'Bot profile: {bot_profile}', self._get_log_extra_data())

            # TODO: Remove in future
            while True:
                await asyncio.sleep(3)
                logger.info(f'Bot {self._bot.login} sleeping...', self._get_log_extra_data())

    def _get_log_extra_data(self) -> dict:
        return {'account': self._bot.login}


class BotManager:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    async def run_bots(self, bots: List[Account]):
        logger.debug(f'Running bots: {bots}')
        for bot in bots:
            if bot.login not in self._tasks.keys():
                await self._create_task(bot)
                await self._tasks[bot.login]

    def stop_bots(self, bots: List[Account]):
        logger.debug(f'Run bots: {bots}')
        for bot in bots:
            self._tasks[bot.login].cancel()
            self._tasks.pop(bot.login)

    async def _create_task(self, bot: Account):
        bot_workflow = BotWorkflow(bot)

        task = asyncio.create_task(bot_workflow.run())
        task.set_name(bot.login)
        self._tasks[bot.login] = task

        logger.debug(f'Create task: {task}')
