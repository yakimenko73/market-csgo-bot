from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

MARKET_LINK = f'https://{settings.MARKET_SETTINGS.host}/?s=price&r=&q=&search='

HOLD = 33554432
NOT_AT_HOLD = 16777216
HOLD_STATUSES = [
    (HOLD, 'Hold'),
    (NOT_AT_HOLD, 'NotAtHold'),
]

NEW = 65536
NOT_AT_STEAM_INV = 131072
CHECK = 262144
STATUSES = [
    (NEW, 'New'),
    (NOT_AT_STEAM_INV, 'NotAtSteamInv'),
    (CHECK, 'Check'),
]

GOOGLE_885 = 1
GOOGLE_886 = 2
GOOGLE_888 = 16
CASINO = 5
UNKNOWN = 8
PLACES = [
    (GOOGLE_885, 'Google885'),
    (GOOGLE_886, 'Google886'),
    (GOOGLE_888, 'Google888'),
    (CASINO, 'Casino'),
    (UNKNOWN, 'Unknown'),
]

YES = 256
NO = 512
WAIT = 1024
CORRECT_NAMES = [
    (YES, 'Yes'),
    (NO, 'No'),
    (WAIT, 'Wait'),
]

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


class AccountItem(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    market_hash_name = models.CharField(max_length=120)
    market_ru_name = models.CharField(max_length=120)
    market_eu_link = models.URLField(max_length=99, blank=True)
    market_ru_link = models.URLField(max_length=99, blank=True)
    google_price_usd = models.FloatField()
    google_drive_time = models.DateTimeField()
    steam_price_usd = models.DecimalField(max_digits=6, decimal_places=2)
    steam_time = models.DateTimeField()
    status = models.BigIntegerField(choices=STATUSES, default=None)
    place = models.IntegerField(choices=PLACES, default=None)
    hold = models.DateTimeField()
    hold_status = models.BigIntegerField(choices=HOLD_STATUSES, default=None)
    asset_id = models.BigIntegerField()
    trade_id = models.CharField(max_length=30)
    drive_discount = models.CharField(max_length=30)
    drive_discount_percent = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal(0),
                                                 validators=PERCENTAGE_VALIDATOR)
    correct_name = models.IntegerField(choices=CORRECT_NAMES, default=None)
    item_price_usd = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0)
    item_price_ru = models.DecimalField(max_digits=6, decimal_places=2, blank=True, default=0)

    def save(self, *args, **kwargs):
        if not self.market_eu_link:
            self.market_eu_link = MARKET_LINK + self.market_hash_name
        if not self.market_ru_link:
            self.market_ru_link = MARKET_LINK + self.market_ru_name
        super(AccountItem, self).save(*args, **kwargs)
