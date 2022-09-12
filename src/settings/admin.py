from django.contrib import admin
from django.contrib.sites.models import Site
from preferences.admin import PreferencesAdmin

from .models import BotPreferences

admin.site.unregister(Site)


@admin.register(BotPreferences)
class PreferenceAdmin(PreferencesAdmin):
    exclude = ['sites']
