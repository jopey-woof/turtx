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

# Wait for Turtle Dashboard (port 8080)
echo "🏠 Waiting for Turtle Dashboard..."
RETRY_COUNT=0
while ! curl -s http://localhost:8080 > /dev/null; do
    sleep 5
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -gt 24 ]; then
        echo "⚠️ Starting anyway..."
        break
    fi
done
echo "✅ Turtle Dashboard ready"

# Display settings
xset -dpms || true
xset s off || true
echo "✅ Display configured"

sleep 2

echo "🌐 Starting Chrome..."

# Create chrome directory properly
mkdir -p /home/shrimp/.chrome-kiosk/Default

# Ensure preferences are set to skip welcome screen
if [ ! -f /home/shrimp/.chrome-kiosk/Default/Preferences ]; then
    echo "⚠️ Creating Chrome preferences..."
    cat > /home/shrimp/.chrome-kiosk/Default/Preferences << 'EOF'
{
  "browser": {
    "show_home_button": false,
    "window_placement": {
      "maximized": true
    },
    "check_default_browser": false,
    "should_reset_check_default_browser": false
  },
  "distribution": {
    "suppress_first_run_default_browser_prompt": true,
    "suppress_first_run_ui": true
  },
  "first_run_complete": true,
  "suppress_first_run_default_browser_prompt": true,
  "suppress_first_run_ui": true,
  "session": {
    "restore_on_startup": 4,
    "startup_urls": ["http://localhost:8080"]
  },
  "startup": {
    "startup_urls": ["http://localhost:8080"]
  }
}
EOF
fi

# Start Chrome with enhanced flags to skip welcome screen
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
    --disable-frame-rate-limit \
    --disable-gpu-vsync \
    --disable-accelerated-2d-canvas \
    --disable-accelerated-jpeg-decoding \
    --disable-accelerated-mjpeg-decode \
    --disable-accelerated-video-decode \
    --disable-accelerated-video-encode \
    --disable-gpu-rasterization \
    --disable-software-rasterizer \
    --disable-background-media-suspend \
    --disable-background-video-track \
    --disable-background-timer-throttling \
    --disable-renderer-backgrounding \
    --disable-backgrounding-occluded-windows \
    --disable-features=TranslateUI \
    --disable-ipc-flooding-protection \
    "http://localhost:8080" 2>/dev/null 