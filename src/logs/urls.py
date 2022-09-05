from django.urls import path

from .views import kibana_stream, kibana_dashboards

urlpatterns = [
    path('', kibana_stream),
    path('dashboards', kibana_dashboards)
]
