#!/bin/bash

# Turtle Monitor System - Cleanup Script
# Removes old files and ensures system stays clean

set -e

echo "🧹 Turtle Monitor System Cleanup"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "📋 Checking for old files and services..."

# 1. Remove old systemd services
echo "🔧 Cleaning up old systemd services..."
if [ -f "/etc/systemd/system/kiosk.service" ]; then
    echo "  - Removing old kiosk.service"
    systemctl stop kiosk.service 2>/dev/null || true
    systemctl disable kiosk.service 2>/dev/null || true
    rm -f /etc/systemd/system/kiosk.service
fi

if [ -f "/etc/systemd/system/turtle-kiosk.service" ]; then
    echo "  - Removing old turtle-kiosk.service"
    systemctl stop turtle-kiosk.service 2>/dev/null || true
    systemctl disable turtle-kiosk.service 2>/dev/null || true
    rm -f /etc/systemd/system/turtle-kiosk.service
fi

# Reload systemd
systemctl daemon-reload

# 2. Clean up old Chrome processes
echo "🌐 Cleaning up old Chrome processes..."
pkill -f "localhost:8123" 2>/dev/null || true
pkill -f "direct-kiosk.html" 2>/dev/null || true

# 3. Clean up old files
echo "📁 Cleaning up old files..."

# Create disabled directories if they don't exist
mkdir -p /home/shrimp/turtx/homeassistant/www/disabled
mkdir -p /home/shrimp/turtle-monitor/disabled

# Move old kiosk files to disabled
if [ -f "/home/shrimp/turtx/kiosk/start-kiosk.sh" ]; then
    echo "  - Moving old start-kiosk.sh to disabled"
    mv /home/shrimp/turtx/kiosk/start-kiosk.sh /home/shrimp/turtx/kiosk/start-kiosk.sh.disabled
fi

# Move old Home Assistant kiosk files
for file in /home/shrimp/turtx/homeassistant/www/*.html; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        if [[ "$filename" == *"kiosk"* ]] || [[ "$filename" == *"login"* ]] || [[ "$filename" == *"dashboard"* ]]; then
            echo "  - Moving $filename to disabled"
            mv "$file" /home/shrimp/turtx/homeassistant/www/disabled/
        fi
    fi
done

# 4. Clean up old turtle-monitor directory
if [ -d "/home/shrimp/turtle-monitor/kiosk" ]; then
    echo "  - Moving old turtle-monitor kiosk to disabled"
    mv /home/shrimp/turtle-monitor/kiosk /home/shrimp/turtle-monitor/disabled/
fi

# 5. Clean up Chrome cache
echo "🧹 Cleaning Chrome cache..."
rm -rf /home/shrimp/.chrome-kiosk/* 2>/dev/null || true
rm -rf /tmp/.com.google.Chrome* 2>/dev/null || true

# 6. Verify current services are running
echo "✅ Verifying current services..."

if systemctl is-active --quiet turtle-monitor-kiosk.service; then
    echo "  - turtle-monitor-kiosk.service: ✅ RUNNING"
else
    echo "  - turtle-monitor-kiosk.service: ❌ NOT RUNNING"
    echo "    Starting service..."
    systemctl start turtle-monitor-kiosk.service
fi

# 7. Check for any remaining conflicting processes
echo "🔍 Checking for remaining conflicts..."
conflicting_processes=$(ps aux | grep -E "(localhost:8123|direct-kiosk)" | grep -v grep || true)
if [ -n "$conflicting_processes" ]; then
    echo "  ⚠️  Found conflicting processes:"
    echo "$conflicting_processes"
    echo "  - Killing conflicting processes..."
    pkill -f "localhost:8123" 2>/dev/null || true
    pkill -f "direct-kiosk" 2>/dev/null || true
else
    echo "  ✅ No conflicting processes found"
fi

# 8. Final status check
echo "📊 Final Status Check"
echo "===================="

echo "Active Services:"
systemctl list-units --type=service --state=running | grep -E "(turtle|kiosk)" || echo "  No turtle/kiosk services found"

echo ""
echo "Chrome Processes:"
ps aux | grep chrome | grep -v grep | grep localhost:8000 || echo "  No turtle monitor Chrome process found"

echo ""
echo "API Health:"
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "  ✅ Turtle Monitor API: HEALTHY"
else
    echo "  ❌ Turtle Monitor API: NOT RESPONDING"
fi

echo ""
echo "🎉 Cleanup Complete!"
echo "==================="
echo "✅ Old services removed"
echo "✅ Conflicting files moved to disabled directories"
echo "✅ Chrome cache cleared"
echo "✅ Current services verified"
echo ""
echo "The Turtle Monitor Kiosk should now be running cleanly."
echo "Check the touchscreen to verify it's displaying correctly." 