from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from preferences.models import Preferences

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


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
