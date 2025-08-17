#!/bin/bash

# Turtle Kiosk Startup Script - Stable Version
set -e

echo "🐢 Starting Turtle Kiosk (Stable Mode)..."

export DISPLAY=:0
export HOME=/home/shrimp
export USER=shrimp

echo "✅ Environment configured"

# Kill any existing processes
pkill -f "chrome\|openbox" || true
sleep 3

# Clear Chrome cache and data
rm -rf /home/shrimp/.chrome-kiosk/* || true
rm -rf /tmp/.com.google.Chrome* || true

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

echo "🌐 Starting Chrome (Stable Mode)..."

# Create chrome directory properly
mkdir -p /home/shrimp/.chrome-kiosk

# Start Chrome with more restrictive settings
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
    --disable-background-timer-throttling \
    --disable-backgrounding-occluded-windows \
    --disable-renderer-backgrounding \
    --disable-features=TranslateUI \
    --disable-ipc-flooding-protection \
    --disable-default-apps \
    --disable-extensions \
    --disable-plugins \
    --disable-sync \
    --no-first-run \
    --no-default-browser-check \
    --disable-component-update \
    --disable-background-networking \
    --disable-client-side-phishing-detection \
    --disable-hang-monitor \
    --disable-prompt-on-repost \
    --disable-domain-reliability \
    --disable-features=VizDisplayCompositor \
    --force-color-profile=srgb \
    --metrics-recording-only \
    --no-report-upload \
    --disable-background-timer-throttling \
    --disable-backgrounding-occluded-windows \
    --disable-renderer-backgrounding \
    --disable-features=TranslateUI \
    --disable-ipc-flooding-protection \
    "http://localhost:8123" 2>/dev/null 