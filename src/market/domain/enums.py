from enum import Enum


class MarketUrls(Enum):
    PING = '/api/v2/ping'
    TEST = '/api/v2/test'
    SET_STEAM_API_KEY = '/api/v2/set-steam-api-key'
    GET_INVENTORY = '/api/v2/my-inventory'
    UPDATE_INVENTORY = '/api/v2/update-inventory'
    GET_ITEMS_BY_HASH_NAME = '/api/v2/search-list-items-by-hash-name-all'
