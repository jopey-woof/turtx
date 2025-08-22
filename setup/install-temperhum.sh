#!/bin/bash

# 🐢 TEMPerHUM Sensor Installation Script
# This script installs and configures the TEMPerHUM USB sensor system

set -e

echo "🐢 TEMPerHUM Sensor Installation"
echo "================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Check if we're on the remote machine (allow SSH execution)
if [[ "$(hostname)" != "turtle-monitor" ]] && [[ "$(hostname)" != "beelink" ]] && [[ -z "$SSH_CLIENT" ]]; then
    echo "❌ This script should be run on the remote turtle monitoring machine"
    echo "SSH to the remote machine first: ssh shrimp@10.0.20.69"
    exit 1
fi

echo "✅ Running on correct machine"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
echo shrimp | sudo -S apt update
echo shrimp | sudo -S apt install -y python3-pip python3-evdev python3-paho-mqtt

# Install additional system packages
echo "🔧 Installing system packages..."
echo shrimp | sudo -S apt install -y mosquitto-clients

# Create log file with proper permissions
echo "📝 Setting up logging..."
echo shrimp | sudo -S touch /var/log/temperhum-manager.log
echo shrimp | sudo -S chown shrimp:shrimp /var/log/temperhum-manager.log
echo shrimp | sudo -S chmod 644 /var/log/temperhum-manager.log

# Install udev rules
echo "🔌 Installing udev rules..."
echo shrimp | sudo -S cp hardware/99-temperhum.rules /etc/udev/rules.d/
echo shrimp | sudo -S udevadm control --reload-rules
echo shrimp | sudo -S udevadm trigger

# Install systemd service
echo "⚙️  Installing systemd service..."
echo shrimp | sudo -S cp hardware/temperhum-manager.service /etc/systemd/system/
echo shrimp | sudo -S systemctl daemon-reload
echo shrimp | sudo -S systemctl enable temperhum-manager.service

# Create data directory
echo "📁 Creating data directories..."
mkdir -p /tmp/temperhum_data
chmod 755 /tmp/temperhum_data

# Add user to input group for device access
echo "👤 Setting up user permissions..."
echo shrimp | sudo -S usermod -a -G input shrimp

echo ""
echo "✅ TEMPerHUM installation completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Reboot or log out/in to apply group changes"
echo "2. Connect TEMPerHUM sensors to USB ports"
echo "3. Start the service: sudo systemctl start temperhum-manager.service"
echo "4. Check status: sudo systemctl status temperhum-manager.service"
echo "5. Monitor logs: sudo journalctl -u temperhum-manager.service -f"
echo ""
echo "🔍 Testing commands:"
echo "  # Check if sensors are detected"
echo "  lsusb | grep -i temperhum"
echo "  ls /dev/input/event*"
echo ""
echo "  # Monitor MQTT topics"
echo "  mosquitto_sub -t 'turtle/sensors/temperhum/#'"
echo ""
echo "  # Check service status"
echo "  sudo systemctl status temperhum-manager.service" 