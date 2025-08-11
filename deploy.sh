#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Run docker compose (detached)
docker-compose up -d

# Paths for systemd units - adjust if needed
SYSTEMD_DIR="/etc/systemd/system"

echo "Copying systemd unit files..."
sudo cp agent.service "$SYSTEMD_DIR/"
sudo cp agent.timer "$SYSTEMD_DIR/"

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting agent.timer..."
sudo systemctl enable --now agent.timer

echo "Done."
