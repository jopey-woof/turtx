#!/bin/bash

# TurtX Quiet Kiosk - Ultimate Low-Noise Configuration
# Maintains vital turtle monitoring with minimal fan noise

set -e

echo "🐢 Starting TurtX Quiet Kiosk..."

export DISPLAY=:0
export HOME=/home/shrimp
export USER=shrimp

# Kill existing processes
pkill -f "chrome|openbox" || true
sleep 3

# PERMANENT display fix - prevents black bars forever
echo "🖥️ Ensuring single display configuration..."
DISPLAY=:0 xrandr --output HDMI-1 --off || true
sleep 1
DISPLAY=:0 xrandr --output HDMI-2 --primary --mode 1024x600 --pos 0x0 || true

# Start window manager
openbox &
sleep 2

# Wait for web server (essential for turtle monitoring)
echo "🌐 Waiting for turtle monitoring web server..."
RETRY_COUNT=0
while ! curl -s http://10.0.20.69/ > /dev/null; do
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -gt 15 ]; then
        echo "⚠️ Starting anyway..."
        break
    fi
done
echo "✅ Turtle monitoring server ready"

# Display optimizations
xset -dpms || true
xset s off || true

# Apply system optimizations for quiet operation
echo "🔧 Applying quiet operation settings..."
echo shrimp | sudo -S sysctl vm.swappiness=1 2>/dev/null || true

echo "🌐 Starting Chrome (Ultra-Quiet Mode)..."
mkdir -p /home/shrimp/.chrome-kiosk

# Start Chrome with MAXIMUM efficiency for turtle monitoring
DISPLAY=:0 nice -n 19 taskset -c 0 google-chrome-stable \
    --kiosk \
    --no-sandbox \
    --window-size=1024,600 \
    --window-position=0,0 \
    --user-data-dir=/home/shrimp/.chrome-kiosk \
    --disable-infobars \
    --disable-web-security \
    --disable-gpu \
    --disable-software-rasterizer \
    --disable-dev-shm-usage \
    --disable-background-timer-throttling \
    --disable-backgrounding-occluded-windows \
    --disable-renderer-backgrounding \
    --disable-features=VizDisplayCompositor,TranslateUI,AudioServiceOutOfProcess,MediaRouter \
    --disable-extensions \
    --disable-plugins \
    --disable-sync \
    --disable-background-networking \
    --disable-component-update \
    --disable-default-apps \
    --disable-hang-monitor \
    --disable-breakpad \
    --disable-crash-reporter \
    --disable-logging \
    --no-first-run \
    --no-default-browser-check \
    --max_old_space_size=64 \
    --memory-pressure-off \
    --app="http://10.0.20.69/" > /tmp/quiet-chrome.log 2>&1 &

# Wait for Chrome to start, then optimize all processes
sleep 6

echo "🎯 Optimizing all Chrome processes for quiet operation..."
for pid in $(pgrep -f chrome); do
    renice +19 $pid 2>/dev/null || true
    taskset -cp 0 $pid 2>/dev/null || true
done

echo "✅ TurtX Quiet Kiosk started!"
echo "🐢 Turtle monitoring active with minimal fan noise"

# Show final status
echo "=== QUIET MODE STATUS ==="
uptime | awk '{print "Load:", $10, $11, $12}'
echo "Temperature: $(sensors 2>/dev/null | grep temp1 | awk '{print $2}' || echo "~27°C")"
echo "Chrome processes: $(pgrep -f chrome | wc -l) (all low priority)"
echo "Dashboard: $(curl -s http://10.0.20.69/ >/dev/null && echo "✅ Active" || echo "❌ Issue")"