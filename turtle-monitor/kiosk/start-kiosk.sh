#!/bin/bash

# Turtle Kiosk Startup Script - Simple and Working
set -e

echo "🐢 Starting Turtle Kiosk..."

export DISPLAY=:0
export HOME=/home/shrimp
export USER=shrimp

echo "✅ Environment configured"

# Kill any existing processes
pkill -f "chrome\|openbox" || true
sleep 2

# Ensure only touchscreen is active
xrandr --output HDMI-1 --off || true
xrandr --output HDMI-2 --primary --mode 1024x600 || true
echo "✅ Touchscreen configured"

# Start Openbox
openbox &
echo "✅ Window manager started"
sleep 3

# Wait for Home Assistant
echo "🏠 Waiting for Home Assistant..."
RETRY_COUNT=0
while ! curl -s http://localhost:8123 > /dev/null; do
    sleep 5
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -gt 24 ]; then
        echo "⚠️ Starting anyway..."
        break
    fi
done
echo "✅ Home Assistant ready"

# Display settings
xset -dpms || true
xset s off || true
echo "✅ Display configured"

sleep 2

echo "🌐 Starting Chrome..."

# Create chrome directory properly
mkdir -p /home/shrimp/.chrome-kiosk

# Start Chrome
exec google-chrome-stable \
    --kiosk \
    --no-sandbox \
    --disable-dev-shm-usage \
    --window-size=1024,600 \
    --start-fullscreen \
    --user-data-dir=/home/shrimp/.chrome-kiosk \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-translate \
    --disable-web-security \
    "http://localhost:8080/index.html" 2>/dev/null
