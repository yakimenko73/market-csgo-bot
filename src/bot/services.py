import logging

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

    async def run_workflow(self):
        dict_ = model_to_dict(self._bot)
        proxy_creds = ProxyCredentials.parse_str(self._bot.proxy)
        steam_creds = SteamCredentials.parse_obj(dict_).with_guard(**dict_)

        steam_api = SteamApi(steam_creds, ClientSession(connector=ProxyConnector(**proxy_creds.dict())))
        async with steam_api as steam:
            logger.info('Bot workflow start successfully', extra={'account': self._bot.login})
            logger.info(f'Login alive: {steam.logged_in()}')
