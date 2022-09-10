from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from src.common.models import SingletonModel

PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]


class Settings(SingletonModel):
    currency_rate = models.FloatField()
    min_profit = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(10),
                                     validators=PERCENTAGE_VALIDATOR)
    max_profit = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(100),
                                     validators=PERCENTAGE_VALIDATOR)

    def __str__(self):
        return 'Main bot settings'

    class Meta:
        verbose_name_plural = 'Main bot settings'
