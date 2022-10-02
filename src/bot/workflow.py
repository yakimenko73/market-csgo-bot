import asyncio
import itertools
import logging
from asyncio import Task
from typing import List, Tuple

from asgiref.sync import sync_to_async
from django.forms import model_to_dict
from preferences import preferences

from bot.constants import *
from common.http.client import AsyncHttpClient
from common.models import ProxyCredentials
from common.utils import get_log_extra as extra, invoke_forever, invoke_until, to_chunks
from market.api import MarketApi
from market.domain.constants import GET_ITEMS_BY_HASH_NAME_LIMIT, BAD_KEY_ERROR_MESSAGE
from market.domain.models import MarketCredentials, GetItemsByHashNameResponse
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

        self._market_keys = None
        self._market_prices = {}

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
        self._market_keys = await sync_to_async(lambda: itertools.cycle(self.get_market_keys()))()
        tasks = [self._create_task(key, chunk) for key, chunk in zip(self._market_keys, hash_chunks)]

        for task in asyncio.as_completed(tasks):
            response = await task
            for hash_name, data in response.data.items():
                self._market_prices[hash_name] = data[0].price

        logger.info(f'Collecting market prices finish: {self._market_prices}', extra=extra(self._bot.login))

    def _create_task(self, key: str, hash_names: Tuple[str]) -> Task:
        task = asyncio.create_task(self._collect_prices_task(key, hash_names))
        task.set_name(key)
        return task

    async def _collect_prices_task(self, key: str, hash_names: Tuple[str]) -> GetItemsByHashNameResponse:
        response = await self._market_api.get_items_by_hash_name(key, hash_names)
        if await self._has_bad_key_error(key, response):
            for new_key in self._market_keys:
                if new_key != key:
                    logger.info(f'Switch to another key: {new_key}', extra=extra(self._bot.login))
                    response = await self._market_api.get_items_by_hash_name(new_key, hash_names)
                    if not await self._has_bad_key_error(key, response):
                        break
        return response

    async def _has_bad_key_error(self, key: str, response: GetItemsByHashNameResponse) -> bool:
        has_error = False
        if response.error == BAD_KEY_ERROR_MESSAGE:
            has_error = True
            logger.warning(f'Bad key error for {key} key', extra=extra(self._bot.login))
            await self.deactivate_market_key(key)
        return has_error

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

    @sync_to_async
    def deactivate_market_key(self, key: str):
        logger.info(f'Deactivate market key: {key}', extra=extra(self._bot.login))
        Key.objects.filter(key=key).update(active=False)
