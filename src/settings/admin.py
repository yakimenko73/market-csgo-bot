from django.contrib import admin

from .models import Settings


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = (
        'currency_rate',
        'min_profit',
        'max_profit',
    )
