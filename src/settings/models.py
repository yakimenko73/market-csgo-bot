from decimal import Decimal

from django.db import models
from preferences.models import Preferences

from common.validators import PERCENTAGE_VALIDATOR


class BotPreferences(Preferences):
    currency_rate = models.FloatField(default=0)
    min_profit = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(10),
                                     validators=PERCENTAGE_VALIDATOR)
    max_profit = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(100),
                                     validators=PERCENTAGE_VALIDATOR)

    def __str__(self):
        return 'Bot preferences'

    class Meta:
        verbose_name_plural = 'Bot preferences'
