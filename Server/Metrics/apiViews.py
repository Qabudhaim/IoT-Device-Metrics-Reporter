import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Device, SystemMetrics, NetworkMetrics
from .serializers import DeviceSerializer, SystemMetricsSerializer, NetworkMetricsSerializer

# Configure logger for this module
logger = logging.getLogger(__name__)

def build_response(status_text: str, message: str, data=None, errors=None, status_code=status.HTTP_200_OK):
    """
    Builds a standardized API response.
    """
    payload = {
        "status": status_text,
        "message": message
    }
    if data is not None:
        payload["data"] = data
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=status_code)

class DeviceListCreateView(APIView):
    """
    API view for listing all devices, creating a new device, and partially updating device metrics.
    """
    def get(self, request):
        logger.info("Fetching all devices")
        devices = Device.objects.all()
        serializer = DeviceSerializer(devices, many=True)
        return build_response(
            status_text="success",
            message="Devices retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        logger.info("Creating a new device with data: %s", request.data)
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            device = serializer.save()
            # Handle system metrics if provided
            system_data = request.data.get("system_metrics")
            if system_data:
                logger.info("Creating system metrics for device %s: %s", device.device_id, system_data)
                system_serializer = SystemMetricsSerializer(data=system_data)
                if system_serializer.is_valid():
                    system_serializer.save(device=device)
                else:
                    logger.error("Invalid system metrics data: %s", system_serializer.errors)
                    return build_response(
                        "error",
                        "Invalid system metrics data",
                        errors=system_serializer.errors,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            # Handle network metrics if provided
            network_data = request.data.get("network_metrics")
            if network_data:
                logger.info("Creating network metrics for device %s: %s", device.device_id, network_data)
                network_serializer = NetworkMetricsSerializer(data=network_data)
                if network_serializer.is_valid():
                    network_serializer.save(device=device)
                else:
                    logger.error("Invalid network metrics data: %s", network_serializer.errors)
                    return build_response(
                        "error",
                        "Invalid network metrics data",
                        errors=network_serializer.errors,
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            logger.info("Device and metrics created successfully for device %s", device.device_id)
            return build_response(
                "success",
                "Device and metrics created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        logger.error("Device creation failed: %s", serializer.errors)
        return build_response(
            "error",
            "Device creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request):
        device_id = request.data.get("device_id")
        if not device_id:
            logger.error("Device ID is required for patching")
            return build_response(
                "error",
                "Device ID is required for patching",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            logger.error("Device not found: %s", device_id)
            return build_response(
                "error",
                "Device not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Update Device fields
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Device updated: %s", device_id)
        else:
            logger.error("Device update failed: %s", serializer.errors)
            return build_response(
                "error",
                "Device update failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Update SystemMetrics if provided
        system_data = request.data.get("system_metrics")
        if system_data:
            try:
                system_metrics = SystemMetrics.objects.get(device=device)
                system_serializer = SystemMetricsSerializer(system_metrics, data=system_data, partial=True)
            except SystemMetrics.DoesNotExist:
                system_serializer = SystemMetricsSerializer(data={**system_data, "device": device.id})
            if system_serializer.is_valid():
                system_serializer.save(device=device)
                logger.info("System metrics updated for device %s", device_id)
            else:
                logger.error("System metrics update failed: %s", system_serializer.errors)
                return build_response(
                    "error",
                    "System metrics update failed",
                    errors=system_serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # Update NetworkMetrics if provided
        network_data = request.data.get("network_metrics")
        if network_data:
            try:
                network_metrics = NetworkMetrics.objects.get(device=device)
                network_serializer = NetworkMetricsSerializer(network_metrics, data=network_data, partial=True)
            except NetworkMetrics.DoesNotExist:
                network_serializer = NetworkMetricsSerializer(data={**network_data, "device": device.id})
            if network_serializer.is_valid():
                network_serializer.save(device=device)
                logger.info("Network metrics updated for device %s", device_id)
            else:
                logger.error("Network metrics update failed: %s", network_serializer.errors)
                return build_response(
                    "error",
                    "Network metrics update failed",
                    errors=network_serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        logger.info("Device and metrics updated successfully for device %s", device_id)
        return build_response(
            "success",
            "Device and metrics updated successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

class DeviceDetailView(APIView):
    """
    API view for retrieving a device and its metrics by device_id.
    """
    def get(self, request, device_id):
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            logger.error("Device not found: %s", device_id)
            return build_response(
                "error",
                "Device not found",
                status_code=status.HTTP_404_NOT_FOUND
            )
        device_data = DeviceSerializer(device).data

        response_data = {
            "device": device_data,
        }
        logger.info("Device and metrics retrieved for device %s", device_id)
        return build_response(
            "success",
            "Device and metrics retrieved successfully",
            data=response_data,
            status_code=status.HTTP_200_OK
        )

class SystemMetricsListCreateView(APIView):
    """
    API view for listing and creating SystemMetrics.
    """
    def get(self, request):
        logger.info("Fetching all system metrics")
        metrics = SystemMetrics.objects.all()
        serializer = SystemMetricsSerializer(metrics, many=True)
        return build_response(
            status_text="success",
            message="System metrics retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        logger.info("Creating new system metrics with data: %s", request.data)
        serializer = SystemMetricsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("System metrics created successfully")
            return build_response(
                status_text="success",
                message="System metrics created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        logger.error("System metrics creation failed: %s", serializer.errors)
        return build_response(
            status_text="error",
            message="System metrics creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class NetworkMetricsListCreateView(APIView):
    """
    API view for listing and creating NetworkMetrics.
    """
    def get(self, request):
        logger.info("Fetching all network metrics")
        metrics = NetworkMetrics.objects.all()
        serializer = NetworkMetricsSerializer(metrics, many=True)
        return build_response(
            status_text="success",
            message="Network metrics retrieved successfully",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    def post(self, request):
        logger.info("Creating new network metrics with data: %s", request.data)
        serializer = NetworkMetricsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Network metrics created successfully")
            return build_response(
                status_text="success",
                message="Network metrics created successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        logger.error("Network metrics creation failed: %s", serializer.errors)
        return build_response(
            status_text="error",
            message="Network metrics creation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
