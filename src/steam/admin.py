from decimal import Decimal

from daterangefilter.filters import DateRangeFilter
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html_join, format_html
from preferences import preferences

from .models import Account, Item, ItemsFile

HREF_URI_PATTERN = "<a href='{}' target=_blank>{}</a>"
MARKET_HASH_NAME_PATTERN = "{links} {name}"
ITEM_PRICE_PATTERN = "<text>{ru_price}₽({usd_price}$)</text>"
MARKET_LINK = f'https://{settings.MARKET_SETTINGS.host}/?s=price&r=&q=&search='


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'login',
        'steam_id',
        'steam_api',
        'google_drive_id',
        'proxy',
    )
    search_fields = (
        'login',
        'steam_id',
        'steam_api',
        'google_drive_id',
        'proxy',
    )


@admin.register(Item)
class AccountItemAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'market_name',
        'google_price',
        'google_drive_time',
        'steam_price',
        'steam_time',
        'status',
        'place',
        'hold',
        'hold_status',
        'asset_id',
        'trade_id',
        'drive_discount',
        'correct_name',
    )
    list_filter = (
        'place',
        'correct_name',
        'status',
        'hold_status',
        ('google_drive_time', DateRangeFilter),
        ('hold', DateRangeFilter),
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

    steam_price.admin_order_field = 'steam_price_usd'
    google_price.admin_order_field = 'google_price_usd'
    market_name.admin_order_field = 'market_hash_name'


admin.site.register(ItemsFile)
