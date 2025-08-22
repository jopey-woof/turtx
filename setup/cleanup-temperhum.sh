#!/bin/bash

# TemperhUM Sensor Cleanup Script
# Removes all previous TemperhUM sensor implementations

echo "🧹 Cleaning up previous TemperhUM sensor implementations..."

# Remove all TemperhUM-related Python files
echo "Removing Python sensor files..."
rm -f hardware/test_evdev_control.py
rm -f hardware/test_hid_communication.py
rm -f hardware/focus_sensors.py
rm -f hardware/activate_sensors_sudo.py
rm -f hardware/monitor_sensors.py
rm -f hardware/activate_sensors.py
rm -f hardware/simple_data_capture_local.py
rm -f hardware/simple_data_capture.py
rm -f hardware/test-temperhum-local.py
rm -f hardware/temperhum-capture.service
rm -f hardware/hid_controller.py
rm -f hardware/temperhum_manager.py

# Remove udev rules (will recreate with new approach)
echo "Removing old udev rules..."
rm -f hardware/99-temperhum-sensors.rules

# Remove any cached Python files
echo "Cleaning Python cache..."
find hardware/ -name "*.pyc" -delete
find hardware/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove any existing service files
echo "Removing old service files..."
sudo systemctl stop temperhum-capture 2>/dev/null || true
sudo systemctl disable temperhum-capture 2>/dev/null || true
sudo rm -f /etc/systemd/system/temperhum-capture.service

# Clean up any existing MQTT configurations
echo "Cleaning MQTT configurations..."
rm -f homeassistant/sensors.yaml
rm -f homeassistant/temperhum_*.yaml

# Remove documentation
echo "Removing old documentation..."
rm -f README-TEMPERHUM.md

# Clean up any temporary files
echo "Cleaning temporary files..."
rm -f hardware/temp_*.txt
rm -f hardware/sensor_*.log

echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Commit this cleanup to git"
echo "2. Start fresh implementation with new approach"
echo "3. Follow phased development plan" 