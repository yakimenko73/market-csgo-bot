from django.conf import settings
from django.shortcuts import redirect

KIBANA_STREAM_URI = f'http://{settings.ELK_SETTINGS.kibana_host}:5601/app/logs/stream'
KIBANA_DASHBOARDS_URI = f'http://{settings.ELK_SETTINGS.kibana_host}:5601/app/dashboards/list'


def kibana_stream(request):
    return redirect(KIBANA_STREAM_URI)


def kibana_dashboards(request):
    return redirect(KIBANA_DASHBOARDS_URI)
