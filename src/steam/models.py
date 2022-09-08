import json
import logging

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from pydantic import ValidationError

from .domain.enums import Status, HoldStatus, Place, CorrectName
from .domain.models import ItemModel

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
    market_eu_link = models.URLField(max_length=99, blank=True)
    market_ru_link = models.URLField(max_length=99, blank=True)
    google_price_usd = models.FloatField()
    google_drive_time = models.DateTimeField()
    steam_price_usd = models.DecimalField(max_digits=6, decimal_places=2)
    steam_time = models.DateTimeField()
    status = models.BigIntegerField(choices=Status.to_list(), default=None)
    place = models.IntegerField(choices=Place.to_list(), default=None)
    hold = models.DateTimeField()
    hold_status = models.BigIntegerField(choices=HoldStatus.to_list(), default=None)
    asset_id = models.CharField(max_length=30)
    trade_id = models.CharField(max_length=30)
    drive_discount = models.CharField(max_length=30)
    drive_discount_percent = models.CharField(max_length=12)
    correct_name = models.IntegerField(choices=CorrectName.to_list(), default=None)
    item_price_usd = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0)
    item_price_ru = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0)

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
            error_counter = 0
            for item in raw['items']:
                accounts = Account.objects.filter(login=item['bot'])
                if accounts.exists():
                    if model := self._parse_model(item):
                        self._save_item(accounts.first(), model)
                    else:
                        error_counter += 1

            logger.info(f'Parsing validation problems was received: {error_counter}')

    @staticmethod
    def _parse_model(item: dict) -> ItemModel:
        model = None
        try:
            model = ItemModel(**item)
        except ValidationError as ex:
            print(ex)
            logger.warning(f'Parsing validation error', extra={'account': item['bot'], 'error': ex.errors()[0]})

        return model

    @staticmethod
    def _save_item(account: Account, item: ItemModel):
        Item(
            account=account,
            market_ru_name=item.ru_name,
            **item.dict(exclude={'owner_bot', 'bot', 'ru_name'})
        ).save()
