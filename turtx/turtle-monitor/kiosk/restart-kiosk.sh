#!/bin/bash

# Turtle Kiosk Restart Script
echo "🐢 Restarting Turtle Kiosk..."

# Kill existing Chrome processes
pkill -f chrome || true
sleep 2

# Ensure Chrome preferences are set
mkdir -p /home/shrimp/.chrome-kiosk/Default

# Create/update preferences to skip welcome screen
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

# Start Chrome with kiosk mode
export DISPLAY=:0
google-chrome-stable \
    --kiosk \
    --app=http://localhost:8080 \
    --no-sandbox \
    --disable-dev-shm-usage \
    --window-size=1024,600 \
    --start-fullscreen \
    --user-data-dir=/home/shrimp/.chrome-kiosk \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-translate \
    --disable-web-security \
    --no-first-run \
    --no-default-browser-check \
    --disable-default-apps \
    --disable-extensions \
    --disable-plugins \
    --disable-sync \
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
    --disable-ipc-flooding-protection &

echo "✅ Kiosk restarted!" 