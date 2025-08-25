#!/bin/bash

# Turtle Monitor Kiosk Startup Script
set -e

echo "Starting Turtle Monitor Kiosk..."

export DISPLAY=:0
export HOME=/home/shrimp
export USER=shrimp

echo "Environment configured"

# Kill any existing Chrome processes
pkill -f "chrome" || true
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

# Wait for Turtle Monitor API
echo "Waiting for Turtle Monitor API..."
RETRY_COUNT=0
while ! curl -s http://localhost:8000/api/health > /dev/null; do
    sleep 5
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -gt 24 ]; then
        echo "Warning: Turtle Monitor API not responding, starting anyway..."
        break
    fi
done
echo "Turtle Monitor API ready"

# Configure display settings
echo "Configuring display settings..."
xset -dpms || true
xset s off || true
echo "Display configured"

sleep 2

echo "Starting Chrome with Turtle Monitor Kiosk..."

# Set environment variables to suppress dialogs
export CHROME_HEADLESS=1
export CHROME_NO_SANDBOX=1
export CHROME_CRASH_REPORTS_DISABLED=1
export GOOGLE_CHROME_DISABLE_CRASH_REPORTS=1

# Create chrome directory properly
mkdir -p /home/shrimp/.chrome-kiosk

        # Start Chrome with turtle monitor kiosk - simplified for camera compatibility
        exec google-chrome-stable \
            --kiosk \
            --app="http://10.0.20.69" \
            --no-sandbox \
            --disable-dev-shm-usage \
            --window-size=1024,600 \
            --start-fullscreen \
            --user-data-dir=/home/shrimp/.chrome-kiosk \
            --disable-infobars \
            --disable-session-crashed-bubble \
            --disable-translate \
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
            --disable-domain-rereliability \
            --force-color-profile=srgb \
            --metrics-recording-only \
            --no-report-upload \
            --disable-print-preview \
            --disable-save-password-bubble \
            --disable-single-click-autofill \
            --disable-spellcheck-autocorrect \
            --disable-background-media-suspend \
            --disable-background-video-track \
            --disable-crash-reporter \
            --disable-breakpad \
            --disable-logging \
            --silent-launch \
            --disable-features=TranslateUI,VizDisplayCompositor \
            --disable-background-timer-throttling \
            --disable-backgrounding-occluded-windows \
            --disable-renderer-backgrounding \
            --disable-default-browser-check 2>/dev/null 