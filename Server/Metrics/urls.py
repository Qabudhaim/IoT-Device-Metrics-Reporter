from django.urls import path
from .views import  index, show_device
from django.conf.urls.static import static
from .apiViews import DeviceListCreateView, SystemMetricsListCreateView, NetworkMetricsListCreateView, DeviceDetailView
from django.conf import settings

app_name = "Metrics"
urlpatterns = [
    path("", index, name="index"),
    path('show_device/<str:device_id>/', show_device, name='show_device'),
    path("api/system-metrics/", SystemMetricsListCreateView.as_view(), name="system_metrics"),
    path("api/network-metrics/", NetworkMetricsListCreateView.as_view(), name="network_metrics"),
    path("api/devices/", DeviceListCreateView.as_view(), name="devices"),
    path("api/devices/<str:device_id>/", DeviceDetailView.as_view(), name="device_detail"),
]
