import asyncio
import logging
import time
from traceback import format_exc as traceback
from typing import List

from asgiref.sync import sync_to_async
from django.forms import model_to_dict

from bot.contants import MARKET_PING_INTERVAL, MARKET_TEST_INTERVAL, MARKET_SET_STEAM_API_INTERVAL, \
    MARKET_UPDATE_INVENTORY_INTERVAL, MARKET_GET_INVENTORY_INTERVAL
from common.domain.models import ProxyCredentials
from common.http.client import AsyncHttpClient
from common.utils import get_log_extra as extra, invoke_forever
from market.api import MarketApi
from market.domain.models import MarketCredentials
from steam.api import SteamApi
from steam.domain.enums import Status
from steam.domain.models import SteamCredentials
from steam.models import Account, Item

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

                await self.set_steam_api_key_loop()
                await self.run_market_periodic_tasks()
        except Exception as ex:
            logger.error(f'Bot workflow not running by error: {ex}', extra=extra(self._bot.login, traceback()))

    async def set_steam_api_key_loop(self):
        while True:
            logger.info('Trying to set steam api key...', extra=extra(self._bot.login))
            then = time.time()
            response = await self._market_api.set_steam_api_key(self._bot.steam_api)
            if response['success']:
                break
            elapsed = time.time() - then
            await asyncio.sleep(MARKET_SET_STEAM_API_INTERVAL - elapsed)

    # TODO: Remove DRY
    async def update_steam_inventory(self):
        while True:
            logger.info('Trying to update inventory...', extra=extra(self._bot.login))
            then = time.time()
            response = await self._market_api.update_inventory()
            if response['success']:
                break
            elapsed = time.time() - then
            await asyncio.sleep(MARKET_GET_INVENTORY_INTERVAL - elapsed)

        while True:
            logger.info('Trying to get inventory...', extra=extra(self._bot.login))
            then = time.time()
            inventory = await self._market_api.get_inventory()
            if inventory['success']:
                break
            elapsed = time.time() - then
            await asyncio.sleep(MARKET_GET_INVENTORY_INTERVAL - elapsed)

        await self.update_items_status([item['id'] for item in inventory['items']])

    async def run_market_periodic_tasks(self):
        logger.info('Run market periodic tasks', extra=extra(self._bot.login))
        await asyncio.gather(
            invoke_forever(self.update_steam_inventory, MARKET_UPDATE_INVENTORY_INTERVAL),
            invoke_forever(self._market_api.ping, MARKET_PING_INTERVAL),
            invoke_forever(self._market_api.test, MARKET_TEST_INTERVAL),
        )

    @sync_to_async
    def update_items_status(self, items_ids: List[str]):
        count = Item.objects.filter(account=self._bot, status=Status.New.value, asset_id__in=items_ids) \
            .update(status=Status.Wait.value)
        logger.info(f'Wait status update successfully for {count} items', extra(self._bot.login))
