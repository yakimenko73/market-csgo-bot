import json
import logging

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from .domain.enums import Status, HoldStatus, Place, CorrectName
from .domain.models import ItemsJsonModel
from .parsers import ItemParser
from settings.models import BotPreferences

logger = logging.getLogger(__name__)

MARKET_LINK = f'https://{settings.MARKET_SETTINGS.host}/?s=price&r=&q=&search='


class Account(models.Model):
    login = models.CharField(max_length=99, unique=True)
    password = models.CharField(max_length=30)
    steam_id = models.PositiveBigIntegerField(unique=True)
    steam_api = models.CharField(max_length=99)
    shared_secret = models.CharField(max_length=99)
    identity_secret = models.CharField(max_length=99)
    google_drive_id = models.CharField(max_length=99)
    proxy = models.CharField(max_length=99)

    def __str__(self):
        return self.login


class Item(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    market_hash_name = models.CharField(max_length=120)
    market_ru_name = models.CharField(max_length=120)
    market_eu_link = models.CharField(max_length=120, blank=True)
    market_ru_link = models.CharField(max_length=120, blank=True)
    google_price_usd = models.FloatField()
    google_drive_time = models.DateTimeField()
    steam_price_usd = models.DecimalField(max_digits=6, decimal_places=2)
    steam_time = models.DateTimeField()
    status = models.BigIntegerField(choices=Status.to_list(), default=None)
    place = models.IntegerField(choices=Place.to_list(), default=None)
    hold = models.DateTimeField()
    hold_status = models.BigIntegerField(choices=HoldStatus.to_list(), default=None)
    asset_id = models.CharField(max_length=30, primary_key=True)
    trade_id = models.CharField(max_length=30, blank=True)
    drive_discount = models.CharField(max_length=30)
    drive_discount_percent = models.CharField(max_length=12)
    correct_name = models.IntegerField(choices=CorrectName.to_list(), default=None)

    def save(self, *args, **kwargs):
        if not self.market_eu_link:
            self.market_eu_link = MARKET_LINK + self.market_hash_name
        if not self.market_ru_link:
            self.market_ru_link = MARKET_LINK + self.market_ru_name
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.market_hash_name


class ItemsFile(models.Model):
    file = models.FileField(validators=[FileExtensionValidator(allowed_extensions=["json"])])

    def save(self, *args, **kwargs):
        with self.file.open('r') as f:
            raw = json.load(f)
            parser = ItemParser(json_model := ItemsJsonModel(**raw))
            accounts = Account.objects.all()
            items = parser.parse_for_accounts(list(accounts.values_list('login', flat=True)))

            [Item(account=accounts.get(login=item.bot), **item.to_dict()).save() for item in items]

            BotPreferences.objects.all().update(currency_rate=json_model.u)
