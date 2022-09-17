from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from settings import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('grappelli/', include('grappelli.urls')),
    path('logs/', include('logs.urls')),
]

if not settings.SERVER_SETTINGS.debug:
    urlpatterns += re_path(
        r'^static/(?P<path>.*)$', serve, dict(document_root=settings.STATIC_ROOT)
    ),
