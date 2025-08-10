from django.contrib import admin
from .models import NetworkMetrics, SystemMetrics, Device

admin.site.register(Device)
admin.site.register(SystemMetrics)
admin.site.register(NetworkMetrics)