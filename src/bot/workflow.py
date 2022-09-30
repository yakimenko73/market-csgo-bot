import asyncio
import itertools
import logging
from typing import List

from asgiref.sync import sync_to_async
from django.forms import model_to_dict
from preferences import preferences

from bot.contants import *
from common.domain.models import ProxyCredentials
from common.http.client import AsyncHttpClient
from common.utils import get_log_extra as extra, invoke_forever, invoke_until, to_chunks
from market.api import MarketApi
from market.domain.constants import GET_ITEMS_BY_HASH_NAME_LIMIT
from market.domain.models import MarketCredentials
from market.models import Key
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
        logger.info('Trying to start bot workflow...', extra=extra(self._bot.login))
        async with self._steam_api as steam:
            logger.info('Bot workflow start successfully', extra=extra(self._bot.login))
            await self.set_steam_api_key()
            await self.update_steam_inventory()
            await self.collect_market_prices()
            await self.run_market_periodic_tasks()

    @invoke_until(MARKET_SET_STEAM_API_INTERVAL, True)
    async def set_steam_api_key(self):
        logger.info('Trying to set steam api key...', extra=extra(self._bot.login))
        return await self._market_api.set_steam_api_key(self._bot.steam_api)

    async def update_steam_inventory(self):
        logger.info('Trying to update inventory...', extra=extra(self._bot.login))
        await invoke_until(MARKET_GET_INVENTORY_INTERVAL, True)(self._market_api.update_inventory)()

        logger.info('Trying to get inventory...', extra=extra(self._bot.login))
        inventory = await invoke_until(MARKET_GET_INVENTORY_INTERVAL, True)(self._market_api.get_inventory)()

        await self.update_items_status([item.id for item in inventory.items])

    async def collect_market_prices(self):
        logger.info('Trying to collect market prices...', extra=extra(self._bot.login))
        hash_names = await self.get_bot_unique_item_hash_names()
        hash_chunks = to_chunks(hash_names, GET_ITEMS_BY_HASH_NAME_LIMIT)
        keys = await sync_to_async(lambda: itertools.cycle(self.get_market_keys()))()
        tasks = []
        for key, chunk in zip(keys, hash_chunks):
            tasks.append(asyncio.create_task(self._market_api.get_items_by_hash_name(key, chunk)))

        for task in asyncio.as_completed(tasks):
            response = await task
            if response.error:
                print(response)

    async def run_market_periodic_tasks(self):
        logger.info('Run market periodic tasks', extra=extra(self._bot.login))
        await asyncio.gather(
            invoke_forever(MARKET_UPDATE_INVENTORY_INTERVAL)(self.update_steam_inventory)(),
            invoke_forever(MARKET_PING_INTERVAL)(self._market_api.ping)(),
            invoke_forever(MARKET_TEST_INTERVAL)(self._market_api.test)(),
        )

    @sync_to_async
    def update_items_status(self, items_ids: List[str]):
        logger.info('Trying to update items status...', extra=extra(self._bot.login))
        prefs = preferences.BotPreferences
        count = Item.objects.filter(
            account=self._bot,
            status=Status.New.value,
            asset_id__in=items_ids,
        ).update(status=Status.Wait.value, min_profit=prefs.min_profit, max_profit=prefs.max_profit)

        logger.info(f'Wait status update successfully for {count} items', extra(self._bot.login))

    @sync_to_async
    def get_bot_unique_item_hash_names(self) -> List[str]:
        items = Item.objects.filter(account=self._bot)
        return list(items.values_list('market_hash_name', flat=True).distinct())

    @staticmethod
    def get_market_keys() -> List[str]:
        return Key.objects.filter(active=True).values_list('key', flat=True)
