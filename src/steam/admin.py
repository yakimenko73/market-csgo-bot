from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('login', 'steam_id', 'steam_api', 'google_drive_id', 'proxy')
    search_fields = ('login', 'steam_id', 'steam_api', 'google_drive_id', 'proxy', 'shared_secret', 'identity_secret')
