from django.contrib import admin
from django.utils.html import format_html
from rangefilter.filters import DateTimeRangeFilter

from .models import Account, AccountItem

HREF_URI_PATTERN = "<a href='{uri}' target=_blank>{uri}</a>"


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
        'shared_secret',
        'identity_secret',
    )


@admin.register(AccountItem)
class AccountItemAdmin(admin.ModelAdmin):
    list_display = (
        'account',
        'market_hash_name',
        'market_ru_name',
        'show_market_eu_link',
        'show_market_ru_link',
        'google_price_usd',
        'google_drive_time',
        'steam_price_usd',
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
        ('google_drive_time', DateTimeRangeFilter),
        ('hold', DateTimeRangeFilter),
    )
    search_fields = (
        'account__login',
        'market_hash_name',
        'asset_id',
        'trade_id',
    )

    @staticmethod
    def show_market_eu_link(obj):
        return format_html(HREF_URI_PATTERN, uri=obj.market_eu_link)

    @staticmethod
    def show_market_ru_link(obj):
        return format_html(HREF_URI_PATTERN, uri=obj.market_ru_link)
