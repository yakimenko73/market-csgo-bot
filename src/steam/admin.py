import asyncio
from decimal import Decimal

from daterangefilter.filters import DateRangeFilter
from django.conf import settings
from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.utils.html import format_html_join, format_html
from preferences import preferences

from bot.manager import BotManager
from common.utils import use_thread
from .models import Account, Item, ItemsFile

HREF_URI_PATTERN = "<a href='{}' target=_blank>{}</a>"
MARKET_HASH_NAME_PATTERN = "{links} {name}"
ITEM_PRICE_PATTERN = "<text>₽{ru_price}(${usd_price})</text>"
ITEM_MARKET_INFO_PATTERN = "<text>{min_price}({profit}%)/{position}/{count}</text>"
ITEM_EXPECTED_PRICES_PATTERN = "<text>{min_price}/{max_price}</text>"
MARKET_LINK = f'{settings.MARKET_SETTINGS.host}/?&sd=asc&s=price&r=&q=&search='


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self._bot_manager = BotManager()

    list_display = (
        'login',
        'steam_id',
        'steam_api',
        'google_drive_id',
        'proxy',
        'is_on',
    )
    search_fields = (
        'login',
        'steam_id',
        'steam_api',
        'google_drive_id',
        'proxy',
    )
    list_filter = ['is_on']
    actions = ['turn_on_bot_account', 'turn_off_bot_account', ]

    @admin.action(description='Turn on selected accounts')
    def turn_on_bot_account(self, request: WSGIRequest, accounts: QuerySet[Account]):
        bots = list(accounts.filter(is_on=False))
        use_thread(lambda: asyncio.run(self._bot_manager.run_bots(bots)))

        accounts.update(is_on=True)

    @admin.action(description='Turn off selected accounts')
    def turn_off_bot_account(self, request: WSGIRequest, accounts: QuerySet[Account]):
        self._bot_manager.stop_bots(list(accounts.filter(is_on=True)))

        accounts.update(is_on=False)


@admin.register(Item)
class AccountItemAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'market_name',
        'market_info',
        'market_time',
        'google_price',
        'google_time',
        'steam_price',
        'steam_time_formatted',
        'status',
        'place',
        'hold_date',
        'asset_id',
        'drive_discount',
        'min_profit',
        'max_profit',
        'expected_prices',
    )
    list_filter = (
        'place',
        'correct_name',
        'status',
        'hold_status',
        ('google_drive_time', DateRangeFilter),
        ('hold', DateRangeFilter),
        'account',
    )
    search_fields = (
        'account__login',
        'market_hash_name',
        'asset_id',
        'trade_id',
    )

    def market_name(self, obj):
        links = [(MARKET_LINK + obj.market_hash_name, 'EU'), (MARKET_LINK + obj.market_ru_name, 'RU')]
        html_links = format_html_join('\n', HREF_URI_PATTERN, (link for link in links))

        return format_html(MARKET_HASH_NAME_PATTERN, links=html_links, name=obj.market_hash_name)

    def google_price(self, obj):
        return format_html(
            ITEM_PRICE_PATTERN,
            ru_price=round(obj.google_price_usd * preferences.BotPreferences.currency_rate, 2),
            usd_price=obj.google_price_usd
        )

    def steam_price(self, obj):
        return format_html(
            ITEM_PRICE_PATTERN,
            ru_price=round(obj.steam_price_usd * Decimal(preferences.BotPreferences.currency_rate), 2),
            usd_price=obj.steam_price_usd
        )

    def market_info(self, obj):
        return format_html(
            ITEM_MARKET_INFO_PATTERN,
            min_price=obj.market_min_price / 100 if obj.market_min_price else '-',
            profit=obj.market_profit or '-',
            position=obj.market_position or '-',
            count=obj.market_count or '-',
        )

    def expected_prices(self, obj):
        return format_html(
            ITEM_EXPECTED_PRICES_PATTERN,
            min_price=obj.expected_min_price.amount if obj.expected_min_price else '-',
            max_price=obj.expected_max_price.amount if obj.expected_max_price else '-',
        )

    @admin.display(description='Steam time')
    def steam_time_formatted(self, obj):
        return obj.steam_time.strftime('%d %H:%M')

    def google_time(self, obj):
        return obj.google_drive_time.strftime('%d %H:%M')

    @admin.display(description='Hold')
    def hold_date(self, obj):
        return obj.hold.strftime('%m/%d')

    steam_price.admin_order_field = 'steam_price_usd'
    steam_time_formatted.admin_order_field = 'steam_time'
    google_price.admin_order_field = 'google_price_usd'
    market_name.admin_order_field = 'market_hash_name'
    google_time.admin_order_field = 'google_drive_time'
    hold_date.admin_order_field = 'hold'
    market_info.admin_order_field = 'market_profit'
    expected_prices.admin_order_field = 'google_price'


admin.site.register(ItemsFile)
