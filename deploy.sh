#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Detect current directory (absolute path)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)/Agent"

# Update agent.service with the correct path
sed -i "s|^WorkingDirectory=.*|WorkingDirectory=$SCRIPT_DIR|" agent.service
sed -i "s|^ExecStart=.*|ExecStart=/usr/bin/python3 $SCRIPT_DIR/main.py|" agent.service

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
