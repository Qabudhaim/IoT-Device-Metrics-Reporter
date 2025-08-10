import os
import re
import time
import subprocess
from typing import Dict, Any, Optional, List
import requests
import uuid
import logging
from decorators import log_exceptions, rate_limiter, retry, log_io

logger = logging.getLogger(__name__)

interval = int(os.environ.get("INTERVAL", 1))  # Default to 1 second if not set
logger.info(f"Metrics collection interval set to {interval} seconds.")

@log_exceptions(default=None)
def get_simulated_id(id_file_path: str = "/tmp/container_id.txt") -> str:
    """
    Generate or read a persistent random container ID, or get from environment if available.

    Args:
        id_file_path (str): Path to store/read the container ID file.

    Returns:
        str: Persistent container ID.
    """
    # Check environment variable first
    env_id = os.environ.get("CONTAINER_ID")
    if env_id:
        logger.info(f"Using device ID from environment: {env_id}")
        return env_id

    if os.path.exists(id_file_path):
        with open(id_file_path, "r") as f:
            container_id = f.read().strip()
            if container_id:
                logger.info(f"Using existing container ID: {container_id}")
                return container_id

    # Generate a new UUID without hyphens
    container_id = str(uuid.uuid4()).replace("-", "")
    with open(id_file_path, "w") as f:
        f.write(container_id)
    logger.info(f"Generated new container ID: {container_id}")
    return container_id

@log_exceptions(default=get_simulated_id())
def get_device_id() -> str:
    try:
        with open('/etc/machine-id', 'r') as f:
            mid = f.read().strip()
            if mid:
                logger.info(f"Successfully retrieved device ID from /etc/machine-id: {mid}")
                return mid
            else:
                logger.warning("Empty /etc/machine-id, falling back to simulated container ID.")
    except FileNotFoundError:
        logger.warning("/etc/machine-id not found, falling back to simulated container ID.")

    return get_simulated_id()

@log_exceptions(default=-1.0)
def get_uptime() -> float:
    """
    Returns system uptime in seconds.
    Returns:
        float: Uptime in seconds, or -1.0 on error.
    """
    with open('/proc/uptime', 'r') as f:
        uptime = float(f.read().split()[0])
        logger.info(f"System uptime retrieved: {uptime} seconds.")
        return uptime

def get_cpu_usage() -> float:
    """
    Estimates CPU usage percentage over a short time interval.
    Reads from /proc/stat and calculates based on active vs total time.
    Returns:
        float: CPU usage percentage, or 0.0 on error.
    """
    def read_cpu_times() -> tuple[int, int]:
        with open('/proc/stat', 'r') as f:
            fields = f.readline().split()[1:]
            fields = list(map(int, fields))
            idle = fields[3]
            total = sum(fields)
            return idle, total

    try:
        idle1, total1 = read_cpu_times()
        time.sleep(0.1)
        idle2, total2 = read_cpu_times()

        idle_delta = idle2 - idle1
        total_delta = total2 - total1

        if total_delta == 0:
            logger.warning("CPU total_delta is zero, returning 0.0 usage.")
            return 0.0

        usage = 100.0 * (1.0 - idle_delta / total_delta)
        logger.info(f"CPU usage calculated: {usage:.2f}%")
        return round(usage, 2)
    except Exception as e:
        logger.exception("Failed to calculate CPU usage.")
        return 0.0

@log_exceptions(default={"%": 0.0, "kB": 0.0, "MB": 0.0, "GB": 0.0})
def get_memory_usage() -> Dict[str, float]:
    """
    Reads /proc/meminfo and returns memory usage in multiple units.
    Returns:
        Dict[str, float]: Dictionary with usage in %, kB, MB, GB.
    """
    with open("/proc/meminfo", "r") as f:
        meminfo = f.read()

    mem_total_kb = int(re.search(r"MemTotal:\s+(\d+)", meminfo).group(1))
    mem_available_kb = int(re.search(r"MemAvailable:\s+(\d+)", meminfo).group(1))

    used_kb = mem_total_kb - mem_available_kb
    used_percent = (used_kb / mem_total_kb) * 100

    logger.info(f"Memory usage calculated: {used_percent:.2f}% ({used_kb} kB used)")

    return {
        "%": round(used_percent, 2),
        "kB": used_kb,
        "MB": round(used_kb / 1024, 2),
        "GB": round(used_kb / 1024**2, 2)
    }

@log_exceptions(default={"%": 0.0, "kB": 0.0, "MB": 0.0, "GB": 0.0})
def get_disk_usage(path: str = "/") -> Dict[str, float]:
    """
    Returns disk usage for the given path in multiple units.
    Args:
        path (str): Filesystem path to check (default is root "/").
    Returns:
        Dict[str, float]: Usage in %, kB, MB, GB.
    """
    stat = os.statvfs(path)
    total = stat.f_blocks * stat.f_frsize
    free = stat.f_bavail * stat.f_frsize
    used = total - free

    used_percent = (used / total) * 100
    used_kb = used // 1024

    logger.info(f"Disk usage for '{path}': {used_percent:.2f}% ({used_kb} kB used)")

    return {
        "%": round(used_percent, 2),
        "kB": used_kb,
        "MB": round(used_kb / 1024, 2),
        "GB": round(used_kb / 1024**2, 2)
    }

@log_exceptions(default=[-1.0, -1.0, -1.0])
def get_load_average() -> List[float]:
    """
    Returns 1, 5, and 15 minute load averages.
    Returns:
        List[float]: Load averages, or [-1.0, -1.0, -1.0] on error.
    """
    with open('/proc/loadavg', 'r') as f:
        fields = f.read().split()[:3]
        load_averages = list(map(float, fields))
        logger.info(f"Load averages retrieved: {load_averages}")
        return load_averages

@log_exceptions(default=None)
def get_default_interface() -> Optional[str]:
    """
    Returns the default network interface (used for internet access).
    Returns:
        Optional[str]: Interface name or None if not found.
    """
    route = subprocess.check_output("ip route show default", shell=True).decode()
    interface = route.split()[4]
    logger.info(f"Default network interface detected: {interface}")
    return interface

@log_exceptions(default=None)
def get_ip_address(interface: str) -> Optional[str]:
    """
    Returns the IP address for a given interface.
    Args:
        interface (str): Network interface name.
    Returns:
        Optional[str]: IPv4 address or None.
    """
    output = subprocess.check_output(f"ip -4 addr show {interface}", shell=True).decode()
    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', output)
    if match:
        ip = match.group(1)
        logger.info(f"IP address for interface '{interface}': {ip}")
        return ip
    else:
        logger.warning(f"No IPv4 address found for interface '{interface}'.")
        return None

@log_exceptions(default=None)
def get_mac_address(interface: str) -> Optional[str]:
    """
    Returns the MAC address for a given interface.
    Args:
        interface (str): Network interface name.
    Returns:
        Optional[str]: MAC address or None.
    """
    with open(f'/sys/class/net/{interface}/address', 'r') as f:
        mac = f.read().strip()
        logger.info(f"MAC address for interface '{interface}': {mac}")
        return mac

def get_network_stats(interface: str) -> Dict[str, int]:
    """
    Returns RX/TX bytes and packets for the given interface.
    Args:
        interface (str): Network interface name.
    Returns:
        Dict[str, int]: RX/TX bytes and packets.
    """
    stats: Dict[str, int] = {
        "rx_bytes": 0,
        "tx_bytes": 0,
        "rx_packets": 0,
        "tx_packets": 0,
    }
    try:
        with open(f'/sys/class/net/{interface}/statistics/rx_bytes') as f:
            stats["rx_bytes"] = int(f.read())
        with open(f'/sys/class/net/{interface}/statistics/tx_bytes') as f:
            stats["tx_bytes"] = int(f.read())
        with open(f'/sys/class/net/{interface}/statistics/rx_packets') as f:
            stats["rx_packets"] = int(f.read())
        with open(f'/sys/class/net/{interface}/statistics/tx_packets') as f:
            stats["tx_packets"] = int(f.read())
        logger.info(
            f"Network stats for interface '{interface}': "
            f"RX bytes={stats['rx_bytes']}, TX bytes={stats['tx_bytes']}, "
            f"RX packets={stats['rx_packets']}, TX packets={stats['tx_packets']}"
        )
    except Exception as e:
        logger.exception(f"Failed to get network stats for interface '{interface}'.")
    return stats

def collect_metrics() -> Dict[str, Any]:
    """
    Collects all relevant system and network metrics.
    Returns:
        Dict[str, Any]: Structured dictionary of metrics.
    """
    logger.info("Starting metrics collection.")

    device_id = get_device_id()
    uptime = get_uptime()
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage('/')
    load_average = get_load_average()
    interface = get_default_interface()

    system_metrics = {
        "uptime": uptime,
        "cpu_usage": cpu_usage,
        'memory_percent': memory_usage['%'],
        "memory_kb": memory_usage['kB'],
        "disk_percent": disk_usage['%'],
        "disk_kb": disk_usage['kB'],
        "load_1": load_average[0],
        "load_5": load_average[1],
        "load_15": load_average[2],
    }

    network_metrics = {
        "interface": interface,
        "ip_address": get_ip_address(interface) if interface else None,
        "mac_address": get_mac_address(interface) if interface else None,
    }

    metrics = {
        "device_id": device_id,
        "system_metrics": system_metrics,
        "network_metrics": network_metrics
    }

    if interface:
        logger.info(f"Collecting network stats for interface '{interface}'.")
        metrics['network_metrics'].update(get_network_stats(interface))
    else:
        logger.warning("No default network interface found; skipping network stats.")

    logger.info("Metrics collection complete.")
    logger.debug(f"Collected metrics: {metrics}")
    return metrics

@retry(max_retries=5, delay=10.0)
@rate_limiter(calls_per_second=1 / interval)
def post_metrics(metrics: Dict[str, Any], url: str) -> Optional[requests.Response]:
    """
    Sends collected metrics to the specified URL using PATCH.
    If the device is not found (404), tries to create it with POST.

    Args:
        metrics (Dict[str, Any]): Metrics dictionary.
        url (str): Endpoint URL.

    Returns:
        Optional[requests.Response]: The response object from the final request, or None on error.
    """
    headers = {"Content-Type": "application/json"}

    response = requests.patch(url, json=metrics, headers=headers)

    if response.status_code == 200:
        logger.info(f"Metrics sent successfully to {url}.")
        return response

    if response.status_code == 404:
        logger.warning("Device not found. Attempting to create device.")
        create_resp = requests.post(url, json=metrics, headers=headers)
        if create_resp.status_code == 201:
            logger.info("Device created and metrics sent successfully.")
        else:
            logger.error(
                f"Failed to create device: {create_resp.status_code} - {create_resp.text}"
            )
        return create_resp

    logger.error(f"Failed to send metrics: {response.status_code} - {response.text}")
    return response

