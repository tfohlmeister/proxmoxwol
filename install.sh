#!/bin/bash
# This script must be run as root

if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root"
  exit 1
fi

# Stop service if it's running
systemctl stop proxmoxwol-vm.service 2>/dev/null || true

# Install files
cp proxmoxwol-listener.py /usr/bin/
chmod 744 /usr/bin/proxmoxwol-listener.py
chown root:root /usr/bin/proxmoxwol-listener.py

cp proxmoxwol-vm.service /etc/systemd/system/
chmod 644 /etc/systemd/system/proxmoxwol-vm.service
chown root:root /etc/systemd/system/proxmoxwol-vm.service

# Reload systemd and enable/restart service
systemctl daemon-reload
systemctl enable proxmoxwol-vm.service
systemctl restart proxmoxwol-vm.service

# Check status
echo "Installation complete. Checking service status..."
systemctl status proxmoxwol-vm.service