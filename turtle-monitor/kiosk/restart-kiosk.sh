#!/bin/bash

# TurtX Kiosk Restart Script
# Simple script to restart the kiosk with proper display configuration

echo "🔄 Restarting TurtX Kiosk..."

# Kill existing Chrome processes
echo "Stopping Chrome..."
pkill -f chrome || true
sleep 3

# Fix display configuration
echo "🖥️ Fixing display..."
export DISPLAY=:0
xrandr --output HDMI-1 --off || true
sleep 1
xrandr --output HDMI-2 --primary --mode 1024x600 --pos 0x0 || true
sleep 1

# Display settings
xset -dpms || true
xset s off || true
echo "✅ Display configured"

# Start Chrome with working configuration
echo "🌐 Starting Chrome..."
mkdir -p /home/shrimp/.chrome-kiosk

DISPLAY=:0 nohup google-chrome-stable \
    --kiosk \
    --no-sandbox \
    --window-size=1024,600 \
    --window-position=0,0 \
    --user-data-dir=/home/shrimp/.chrome-kiosk \
    --disable-infobars \
    --disable-web-security \
    --disable-gpu \
    --app="http://10.0.20.69/" > /tmp/kiosk-restart.log 2>&1 &

sleep 3
echo "✅ TurtX Kiosk restarted!"

# Show status
ps aux | grep chrome | grep app | head -1 || echo "Chrome not running"