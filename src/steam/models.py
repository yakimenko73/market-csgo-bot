import json
import logging

from django.core.validators import FileExtensionValidator
from django.db import models, DatabaseError
from django.db.models import QuerySet

from settings.models import BotPreferences
from .domain.enums import Status, HoldStatus, Place, CorrectName
from .domain.models import ItemsJsonModel, ItemModel
from .parsers import ItemParser

logger = logging.getLogger(__name__)


class Account(models.Model):
    login = models.CharField(max_length=99, unique=True)
    password = models.CharField(max_length=30)
    steam_id = models.PositiveBigIntegerField(unique=True)
    steam_api = models.CharField(max_length=99)
    shared_secret = models.CharField(max_length=99)
    identity_secret = models.CharField(max_length=99)
    google_drive_id = models.CharField(max_length=99)
    proxy = models.CharField(max_length=99)
    is_on = models.BooleanField(default=False)

    def __str__(self):
        return self.login


class Item(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    market_hash_name = models.CharField(max_length=120)
    market_ru_name = models.CharField(max_length=120)
    google_price_usd = models.FloatField()
    google_drive_time = models.DateTimeField()
    steam_price_usd = models.DecimalField(max_digits=6, decimal_places=2)
    steam_time = models.DateTimeField()
    status = models.BigIntegerField(choices=Status.to_list(), default=Status.New.value)
    place = models.IntegerField(choices=Place.to_list(), default=Place.Unknown.value)
    hold = models.DateTimeField()
    hold_status = models.BigIntegerField(choices=HoldStatus.to_list(), default=HoldStatus.Undefined.value)
    asset_id = models.CharField(max_length=30, primary_key=True)
    trade_id = models.CharField(max_length=30, blank=True)
    drive_discount = models.CharField(max_length=30)
    drive_discount_percent = models.CharField(max_length=30)
    correct_name = models.IntegerField(choices=CorrectName.to_list(), default=CorrectName.Yes.value)

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

            [self._save_item(item, accounts) for item in items]

            BotPreferences.objects.all().update(currency_rate=json_model.u)

    @staticmethod
    def _save_item(item: ItemModel, accounts: QuerySet[Account]):
        dict_ = item.to_dict()
        dict_['account_id'] = accounts.get(login=item.bot).id
        try:
            Item.objects.update_or_create(asset_id=item.asset_id, defaults=dict_)
        except DatabaseError as ex:
            logger.warning(f'Db exception for {item.asset_id} item', extra={'account': item.bot, 'error': ex})

    def __str__(self):
        return 'Parsed steam items file'
