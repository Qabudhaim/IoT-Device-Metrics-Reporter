# IoT Device Metrics Reporter

A comprehensive IoT monitoring system that collects and visualizes system metrics from multiple devices in real-time. The system consists of a web-based dashboard for monitoring device metrics and lightweight agents that collect and report system performance data.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Linux system (for deployment scripts)
- Sudo privileges (required for systemd service installation)

### Deployment

1. **Make scripts executable:**
   ```bash
   chmod +x deploy.sh cleanup.sh
   ```

2. **Deploy the system:**
   ```bash
   ./deploy.sh
   ```
   > **Note:** This script requires sudo privileges to install systemd services. The agent will automatically collect and send metrics every 10 seconds.

3. **Access the dashboard:**
   - Open your browser and navigate to `http://localhost:8000`
   - View real-time device metrics and system performance

4. **Cleanup (when needed):**
   ```bash
   ./cleanup.sh
   ```
   > **Note:** This script also requires sudo privileges to remove systemd services.

## 📋 System Overview

The IoT Device Metrics Reporter is a distributed monitoring solution designed for tracking system performance across multiple IoT devices. It provides real-time insights into CPU usage, memory consumption, disk utilization, network statistics, and system load averages.


### Key Features

- **Periodic Monitoring:** Continuous collection and visualization of system metrics (interval configurable via .env)
- **Multi-device Support:** Monitor multiple IoT devices from a centralized dashboard
- **Responsive Web Interface:** Clean, modern UI built with Tailwind CSS
- **RESTful API:** Comprehensive API for device management and metrics collection
- **Containerized Deployment:** Docker-based setup for easy deployment and scaling
- **Device Status Tracking:** Online/offline status monitoring with visual indicators
- **Search & Filter:** Search devices by UUID

## 🏗️ Tech Stack

### Server
- **Backend:** Django 5.2.5 (Python web framework)
- **Database:** PostgreSQL (production) / SQLite (development)
- **API:** Django REST Framework
- **Web Server:** Gunicorn
- **Frontend:** Vanilla JavaScript with Tailwind CSS (CDN)
- **Static Files:** WhiteNoise

### Agent
- **Language:** Python 3
- **HTTP Client:** Requests library
- **System Metrics:** Linux `/proc` filesystem
- **Logging:** Python logging with rotation

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Process Management:** systemd (Linux services)



## 🗄️ Database Models


#### Device
- **UUID:** Primary key (auto-generated)
- **Device ID:** Unique identifier (machine-id or custom)
- **Timestamps:** Created/updated tracking

#### SystemMetrics
- **CPU Usage:** Percentage utilization
- **Memory:** Usage in percentage and KB
- **Disk:** Usage in percentage and KB
- **Load Averages:** 1, 5, and 15-minute averages
- **Uptime:** System uptime in seconds

#### NetworkMetrics
- **Interface Information:** Name, IP, MAC address
- **Traffic Statistics:** RX/TX bytes and packets

## 🌐 API Endpoints

### Device Management
- `GET /api/devices/` - List all devices with latest metrics
- `POST /api/devices/` - Create/update device with metrics
- `GET /api/devices/{uuid}/` - Get specific device details

### Metrics
- `POST /api/devices/{uuid}/system-metrics/` - Submit system metrics
- `POST /api/devices/{uuid}/network-metrics/` - Submit network metrics

### Web Interface
- `/` - Main dashboard
- `/device/{uuid}/` - Detailed device view

## 🔍 Monitoring Features

### Dashboard Capabilities
- **Device Grid View:** Overview of all connected devices
- **Real-time Status:** Online/offline indicators (1-minute threshold)
- **Search Functionality:** Filter devices by UUID
- **Metric Visualization:** Key performance indicators
- **Responsive Design:** Mobile and desktop friendly

### Collected Metrics
- **System Performance:** CPU, memory, disk usage
- **Network Statistics:** Interface-specific traffic data
- **System Health:** Load averages and uptime
- **Device Information:** Unique identifiers and timestamps

### Logging
- **Application Logs:** View detailed logs in the hidden `.log` directory
- **Server Logs:** Located at `Server/.log/metrics.log`
- **Agent Logs:** Located at `Agent/.log/metrics.log` 

## 📝 Development Notes

### Known Limitations
- **Tailwind CDN:** Using CDN mode instead of build process (not production-ready)
- **Machine ID:** Containers use explicit machine-id override
- **Database:** SQLite for development, PostgreSQL for production

### Security Considerations
- Change default Django secret key
- Use environment variables for sensitive data
- Implement proper authentication for production
- Configure firewall rules for exposed ports

## 🚀 Potential Improvements

### Performance & Scalability
1. **WebSocket Implementation**
   - Replace REST API polling with real-time WebSocket connections
   - Reduce server load and network overhead
   - Enable instant metric updates without page refresh
   - Support for real-time alerts and notifications

2. **Frontend Enhancements**
   - Build proper Tailwind CSS pipeline instead of CDN
   - Implement progressive web app (PWA) features
   - Add real-time charts and graphs
   - Mobile-first responsive design improvements

3. **Infrastructure**
   - Add horizontal scaling capabilities
   - Implement load balancing for multiple server instances
   - Add health checks and monitoring
   - Container orchestration with Kubernetes

### Additional Features
- **Alerting System:** Threshold-based notifications
- **Historical Data:** Long-term metric storage and analysis
- **User Authentication:** Multi-user support with role-based access
- **Device Grouping:** Organize devices by location or function
- **Export Capabilities:** CSV/JSON data export functionality
