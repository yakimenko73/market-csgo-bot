from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from .models import Key


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'key',
        'active',
    )

    list_filter = (
        'active',
    )

    actions = ('activate_keys', 'deactivate_keys',)

    @admin.action(description='Activate selected keys')
    def activate_keys(self, request: WSGIRequest, keys: QuerySet[Key]):
        keys.update(active=True)

    @admin.action(description='Deactivate selected keys')
    def deactivate_keys(self, request: WSGIRequest, keys: QuerySet[Key]):
        keys.update(active=False)
