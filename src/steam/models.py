import json
import logging
from decimal import Decimal
from traceback import format_exc as traceback

from django.db import models, DatabaseError
from django.db.models import QuerySet
from djmoney.models.fields import MoneyField
from preferences import preferences

from common.utils import get_log_extra as extra, to_rub
from common.validators import PERCENTAGE_VALIDATOR, JSON_FILE_VALIDATOR
from settings.models import BotPreferences
from .domain.enums import Status, HoldStatus, Place, CorrectName
from .domain.models import ItemsJsonModel, ItemModel
from .parsers import ItemParser

logger = logging.getLogger(__name__)


class Account(models.Model):
    login = models.CharField(max_length=99, unique=True)
    password = models.CharField(max_length=30)
    steam_id = models.PositiveBigIntegerField(unique=True)
    steam_api = models.CharField(max_length=99, unique=True)
    shared_secret = models.CharField(max_length=99)
    identity_secret = models.CharField(max_length=99)
    market_api_key = models.CharField(max_length=99, unique=True)
    google_drive_id = models.CharField(max_length=99, unique=True)
    proxy = models.CharField(max_length=99)
    is_on = models.BooleanField(default=False)

    def __str__(self):
        return self.login


class Item(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    market_hash_name = models.CharField(max_length=120)
    market_ru_name = models.CharField(max_length=120)
    market_id = models.BigIntegerField(blank=True, null=True)
    market_time = models.DateTimeField(blank=True, null=True)
    market_position = models.IntegerField(blank=True, null=True)
    market_min_price = models.IntegerField(blank=True, null=True)
    market_count = models.IntegerField(blank=True, null=True)
    market_profit = models.IntegerField(blank=True, null=True)
    google_price_usd = models.FloatField()
    google_drive_time = models.DateTimeField()
    steam_price_usd = models.DecimalField(max_digits=6, decimal_places=2)
    steam_time = models.DateTimeField()
    status = models.BigIntegerField(choices=Status.to_list(), default=Status.Check.value)
    place = models.IntegerField(choices=Place.to_list(), default=Place.Unknown.value)
    hold = models.DateTimeField()
    hold_status = models.BigIntegerField(choices=HoldStatus.to_list(), default=HoldStatus.Undefined.value)
    asset_id = models.CharField(max_length=30, primary_key=True)
    trade_id = models.CharField(max_length=30, blank=True)
    drive_discount = models.CharField(max_length=30)
    drive_discount_percent = models.CharField(max_length=30)
    correct_name = models.IntegerField(choices=CorrectName.to_list(), default=CorrectName.Yes.value)
    min_profit = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(10),
                                     validators=PERCENTAGE_VALIDATOR)
    max_profit = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(100),
                                     validators=PERCENTAGE_VALIDATOR)
    expected_min_price = MoneyField(max_digits=14, decimal_places=2, null=True, blank=True, default_currency='RUB')
    expected_max_price = MoneyField(max_digits=14, decimal_places=2, null=True, blank=True, default_currency='RUB')

    def __str__(self):
        return self.market_hash_name

    def calculate_expected_prices(self):
        self.expected_min_price = to_rub(self._get_expected_price(self.min_profit), self._get_currency_rate(), 2)
        self.expected_max_price = to_rub(self._get_expected_price(self.max_profit), self._get_currency_rate(), 2)

    def _get_expected_price(self, profit: Decimal) -> float:
        profit_amount = self.google_price_usd / 100 * float(profit)
        return self.google_price_usd + profit_amount

    @staticmethod
    def _get_currency_rate() -> float:
        return preferences.BotPreferences.currency_rate


class ItemsFile(models.Model):
    file = models.FileField(validators=JSON_FILE_VALIDATOR)

    def save(self, *args, **kwargs):
        with self.file.open('r') as f:
            raw = json.load(f)
            parser = ItemParser(json_model := ItemsJsonModel(**raw))
            accounts = Account.objects.all()
            items = parser.parse_for_accounts(list(accounts.values_list('login', flat=True)))

            [self._save_item(item, accounts) for item in items]

            BotPreferences.objects.all().update(currency_rate=json_model.u)

    @staticmethod
    def _save_item(item: ItemModel, accounts: QuerySet[Account]):
        dict_ = item.to_dict()
        dict_['account_id'] = accounts.get(login=item.bot).id
        try:
            Item.objects.update_or_create(asset_id=item.asset_id, defaults=dict_)
        except DatabaseError:
            logger.error(f'Db exception for {item.asset_id} item', extra=extra(item.bot, traceback()))

    def __str__(self):
        return 'Parsed steam items file'
