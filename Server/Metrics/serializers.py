from rest_framework import serializers
from .models import Device, SystemMetrics, NetworkMetrics


class SystemMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetrics
        fields = '__all__'
        extra_kwargs = {
            'device': {'read_only': True}
        }


class NetworkMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkMetrics
        fields = '__all__'
        extra_kwargs = {
            'device': {'read_only': True}
        }


class DeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Device model.

    Serializes the following fields:
    - uuid: Unique identifier for the device.
    - device_id: Device-specific identifier.
    - system_metrics: List of related system metrics, serialized using SystemMetricsSerializer (read-only).
    - network_metrics: List of related network metrics, serialized using NetworkMetricsSerializer (read-only).
    - created_at: Timestamp when the device was created.
    - updated_at: Timestamp when the device was last updated.

    All related metrics fields are read-only and expect multiple entries.
    """
    system_metrics = SystemMetricsSerializer(many=True, read_only=True)
    network_metrics = NetworkMetricsSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = [
            'uuid', 'device_id',
            'system_metrics', 'network_metrics',
            'created_at', 'updated_at'
        ]