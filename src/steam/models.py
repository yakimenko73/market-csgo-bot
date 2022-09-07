import json
from datetime import datetime

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models

from .domain.enums import Status, HoldStatus, Place, CorrectName

MARKET_LINK = f'https://{settings.MARKET_SETTINGS.host}/?s=price&r=&q=&search='

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


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
            for item in raw['items']:
                accounts = Account.objects.filter(login=item['bot'])
                if accounts.exists():
                    print(item)
                    Item(
                        account=accounts.first(),
                        market_hash_name=item['market_hash_name'],
                        market_ru_name=item['ru_name'],
                        google_price_usd=item['google_price_usd'],
                        google_drive_time=datetime.fromtimestamp(item['google_drive_time'] / 1000),
                        steam_price_usd=item['steam_price_usd'],
                        steam_time=datetime.fromtimestamp(item['steam_time'] / 1000),
                        status=item['status'],
                        place=item['place'],
                        hold=datetime.fromtimestamp(item['hold'] / 1000),
                        hold_status=item['hold_status'],
                        asset_id=item['asset_id'],
                        trade_id=item['trade_id'],
                        drive_discount=item['drive_discount'],
                        drive_discount_percent=item['drive_discount_percent'],
                        correct_name=item['correct_name'],
                    ).save()
