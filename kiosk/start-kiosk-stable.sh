#!/bin/bash

# Turtle Kiosk Startup Script - Secure Authentication
set -e

echo "Starting Turtle Kiosk (Secure Authentication)..."

export DISPLAY=:0
export HOME=/home/shrimp
export USER=shrimp

echo "Environment configured"

# Kill any existing processes
pkill -f "chrome\|openbox" || true
sleep 3

# Clear Chrome cache and data
rm -rf /home/shrimp/.chrome-kiosk/* || true
rm -rf /tmp/.com.google.Chrome* || true

# Ensure X server is ready
echo "Configuring display..."
sleep 2

# Configure touchscreen display
xrandr --output HDMI-1 --off || true
xrandr --output HDMI-2 --primary --mode 1024x600 || true
echo "Touchscreen configured"

# Start Openbox window manager
echo "Starting window manager..."
openbox &
OPENBOX_PID=$!
echo "Window manager started (PID: $OPENBOX_PID)"
sleep 3

# Wait for Home Assistant
echo "Waiting for Home Assistant..."
RETRY_COUNT=0
while ! curl -s http://localhost:8123 > /dev/null; do
    sleep 5
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -gt 24 ]; then
        echo "Starting anyway..."
        break
    fi
done
echo "Home Assistant ready"

# Configure display settings
echo "Configuring display settings..."
xset -dpms || true
xset s off || true
echo "Display configured"

sleep 2

echo "Starting Chrome with Secure Kiosk Authentication..."

# Create chrome directory properly
mkdir -p /home/shrimp/.chrome-kiosk

# Start Chrome with secure kiosk authentication
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
    --disable-print-preview \
    --disable-save-password-bubble \
    --disable-single-click-autofill \
    --disable-spellcheck-autocorrect \
    --disable-web-resources \
    --disable-webgl \
    --disable-webgl2 \
    "http://localhost:8123/local/secure-kiosk-login.html" 2>/dev/null 