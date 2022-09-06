from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'TM admin site'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logs/', include('logs.urls')),
]
