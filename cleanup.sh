#!/bin/bash

set -e  # Exit on errors

SYSTEMD_DIR="/etc/systemd/system"

echo "Stopping docker containers..."
docker-compose down

echo "Stopping and disabling agent.timer and agent.service..."
sudo systemctl stop agent.timer agent.service || true
sudo systemctl disable agent.timer agent.service || true

echo "Removing systemd unit files..."
sudo rm -f "$SYSTEMD_DIR/agent.timer" "$SYSTEMD_DIR/agent.service"

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Done."