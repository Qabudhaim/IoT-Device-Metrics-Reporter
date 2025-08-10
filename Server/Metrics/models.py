from django.db import models
import uuid

class Device(models.Model):
    """
    Represents a device entity in the system.

    Fields:
        uuid (UUIDField): Primary key, unique identifier for the device. Automatically generated.
        device_id (CharField): Unique device identifier (max length: 100).
        created_at (DateTimeField): Timestamp when the device was created (auto-set on creation).
        updated_at (DateTimeField): Timestamp when the device was last updated (auto-updated on save).

    Methods:
        __str__(): Returns a string representation of the device, showing the device_id.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=100, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Device ({self.device_id})"


class SystemMetrics(models.Model):
    """
    Model representing system metrics collected from a device.

    Fields:
        device (ForeignKey): Reference to the Device associated with these metrics.
        uptime (FloatField): System uptime in seconds.
        cpu_usage (FloatField): CPU usage percentage.
        memory_percent (FloatField): Memory usage as a percentage.
        memory_kb (BigIntegerField): Memory usage in kilobytes.
        disk_percent (FloatField): Disk usage as a percentage.
        disk_kb (BigIntegerField): Disk usage in kilobytes.
        load_1 (FloatField): System load average over the last 1 minute.
        load_5 (FloatField): System load average over the last 5 minutes.
        load_15 (FloatField): System load average over the last 15 minutes.
        created_at (DateTimeField): Timestamp when the metrics entry was created.
        updated_at (DateTimeField): Timestamp when the metrics entry was last updated.

    Methods:
        __str__(): Returns a human-readable string representation of the metrics entry.
    """
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='system_metrics')

    uptime = models.FloatField()
    cpu_usage = models.FloatField()
    memory_percent = models.FloatField()
    memory_kb = models.BigIntegerField()
    disk_percent = models.FloatField()
    disk_kb = models.BigIntegerField()
    load_1 = models.FloatField()
    load_5 = models.FloatField()
    load_15 = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SystemMetrics for {self.device} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class NetworkMetrics(models.Model):
    """
    Represents network interface metrics for a specific device.

    Attributes:
        device (Device): Reference to the associated Device instance.
        interface (str): Name of the network interface (e.g., 'eth0').
        ip_address (str): IP address assigned to the interface.
        mac_address (str): MAC address of the network interface.
        rx_bytes (int): Number of bytes received on the interface.
        tx_bytes (int): Number of bytes transmitted from the interface.
        rx_packets (int): Number of packets received on the interface.
        tx_packets (int): Number of packets transmitted from the interface.
        created_at (datetime): Timestamp when the metrics record was created.
        updated_at (datetime): Timestamp when the metrics record was last updated.

    Methods:
        __str__(): Returns a human-readable string representation of the network metrics entry.
    """
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='network_metrics')

    interface = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17)

    rx_bytes = models.BigIntegerField()
    tx_bytes = models.BigIntegerField()
    rx_packets = models.BigIntegerField()
    tx_packets = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"NetworkMetrics ({self.interface}) for {self.device} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"