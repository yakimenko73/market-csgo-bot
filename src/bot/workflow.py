import asyncio
import itertools
import logging
from asyncio import Task
from typing import List, Tuple, Iterable, Dict

from asgiref.sync import sync_to_async
from django.forms import model_to_dict
from django.utils import timezone
from preferences import preferences

from bot.constants import *
from common.http.client import AsyncHttpClient
from common.models import ProxyCredentials
from common.utils import get_log_extra as extra, invoke_forever, invoke_until, to_chunks, find_index
from market.api import MarketApi
from market.domain.constants import GET_ITEMS_BY_HASH_NAME_LIMIT, BAD_KEY_ERROR_MESSAGE
from market.domain.models import MarketCredentials, GetItemsByHashNameResponse, MarketItem
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

        self._market_prices_collector = MarketPricesCollector(self._bot, self._market_api)

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

        await self._update_items_status([item.id for item in inventory.items])

    async def collect_market_prices(self):
        logger.info('Trying to collect market prices...', extra=extra(self._bot.login))
        await self._market_prices_collector.collect_market_prices()
        await self._update_item_market_info()
        await self._update_item_market_prices()

    async def run_market_periodic_tasks(self):
        logger.info('Run market periodic tasks', extra=extra(self._bot.login))
        await asyncio.gather(
            invoke_forever(MARKET_UPDATE_INVENTORY_INTERVAL)(self.update_steam_inventory)(),
            invoke_forever(MARKET_COLLECTING_PRICES_INTERVAL)(self.collect_market_prices)(),
            invoke_forever(MARKET_PING_INTERVAL)(self._market_api.ping)(),
            invoke_forever(MARKET_TEST_INTERVAL)(self._market_api.test)(),
        )

    @sync_to_async
    def _update_items_status(self, items_ids: List[str]):
        logger.info('Trying to update items status...', extra=extra(self._bot.login))
        prefs = preferences.BotPreferences
        count = Item.objects.filter(
            account=self._bot,
            status=Status.New.value,
            asset_id__in=items_ids,
        ).update(status=Status.Wait.value, min_profit=prefs.min_profit, max_profit=prefs.max_profit)

        logger.info(f'Wait status update successfully for {count} items', extra(self._bot.login))

    @sync_to_async
    def _update_item_market_info(self):
        prices = self._market_prices_collector.prices
        items = Item.objects.filter(market_hash_name__in=prices.keys(), status__in=Status.get_market_statuses())
        for item in items:
            if item.market_id:
                item.market_position = find_index(item.market_id, prices)

            item.market_time = timezone.now()
            item.market_min_price = self._market_prices_collector.get_item_min_price(item.market_hash_name) / 100
            item.market_count = len(prices[item.market_hash_name])

        Item.objects.bulk_update(items, fields=['market_time', 'market_position', 'market_min_price', 'market_count'])

    @sync_to_async
    def _update_item_market_prices(self):
        prices = self._market_prices_collector.prices
        items = Item.objects.filter(market_hash_name__in=prices.keys(), status__in=Status.get_market_statuses())
        [item.calculate_expected_prices() for item in items]
        Item.objects.bulk_update(items, fields=['expected_min_price', 'expected_max_price'])


class MarketPricesCollector:
    def __init__(self, bot: Account, market_api: MarketApi):
        self._bot = bot
        self._prices = {}
        self._market_api = market_api
        self._market_keys = []

    @property
    def prices(self) -> Dict[str, List[MarketItem]]:
        return self._prices

    async def collect_market_prices(self):
        self._market_keys = await self._get_market_keys_cycle()
        hash_names = await self._get_bot_unique_item_hash_names()
        hash_chunks = to_chunks(hash_names, GET_ITEMS_BY_HASH_NAME_LIMIT)

        logger.info(f'Start collecting prices for {len(hash_names)} items', extra=extra(self._bot.login))
        tasks = [self._create_task(key, chunk) for key, chunk in zip(self._market_keys, hash_chunks)]
        for task in asyncio.as_completed(tasks):
            response = await task
            self._prices.update({hash_name: data for hash_name, data in response.data.items() if response})

        logger.info(f'Finish collecting prices for {len(self._prices.keys())} items', extra=extra(self._bot.login))

    def get_item_min_price(self, hash_name: str) -> float:
        return self._prices[hash_name][0].price

    def _create_task(self, key: str, hash_names: Tuple[str]) -> Task:
        return asyncio.create_task(self._call_api(key, hash_names))

    async def _call_api(self, key: str, hash_names: Tuple[str]) -> GetItemsByHashNameResponse:
        response = await self._market_api.get_items_by_hash_name(key, hash_names)
        if await self._has_error(key, response):
            response = await self._find_working_key(hash_names)
        return response

    async def _find_working_key(self, hash_names: Tuple[str]):
        response = None
        for key in self._market_keys:
            logger.info(f'Switch to another key: {key}', extra=extra(self._bot.login))
            response = await self._market_api.get_items_by_hash_name(key, hash_names)
            if not await self._has_error(key, response):
                break
        return response

    async def _has_error(self, key: str, response: GetItemsByHashNameResponse) -> bool:
        bad_key_error = response.error == BAD_KEY_ERROR_MESSAGE
        if bad_key_error:
            logger.warning(f'Bad key error for {key} key', extra=extra(self._bot.login))
            await self._deactivate_market_key(key)
            self._market_keys.remove(key)
        return bad_key_error

    @sync_to_async
    def _get_market_keys_cycle(self) -> Iterable[str]:
        return itertools.cycle(Key.objects.filter(active=True).values_list('key', flat=True))

    @sync_to_async
    def _get_bot_unique_item_hash_names(self) -> List[str]:
        return list(Item.objects.filter(account=self._bot).values_list('market_hash_name', flat=True).distinct())

    @sync_to_async
    def _deactivate_market_key(self, key: str):
        logger.info(f'Deactivate market key: {key}', extra=extra(self._bot.login))
        Key.objects.filter(key=key).update(active=False)
