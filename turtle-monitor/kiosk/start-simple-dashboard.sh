#!/bin/bash

# TurtX Simple Dashboard Server
# Lightweight HTTP server + kiosk mode without nginx complexity

set -e

PROJECT_DIR="/home/shrimp/turtle-monitor"
DASHBOARD_PORT=8090

echo "🐢 Starting TurtX Simple Dashboard..."

# Kill any existing processes
pkill -f "python.*SimpleHTTPServer\|python.*http.server" || true
pkill -f chrome || true
pkill -f chromium || true
sleep 2

# Set CPU governor to powersave
echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor >/dev/null 2>&1 || true

# Start simple HTTP server for the dashboard
cd "$PROJECT_DIR/frontend"
python3 -m http.server $DASHBOARD_PORT --bind 0.0.0.0 &
HTTP_PID=$!
echo "HTTP server started on port $DASHBOARD_PORT (PID: $HTTP_PID)"

# Wait for server to start
sleep 3

# Start Chrome in efficient kiosk mode
export DISPLAY=:0
export CHROME_FLAGS="
--kiosk
--no-sandbox
--disable-web-security
--disable-gpu
--disable-software-rasterizer
--disable-dev-shm-usage
--disable-extensions
--disable-plugins
--disable-images
--disable-javascript-harmony-shipping
--disable-background-timer-throttling
--disable-renderer-backgrounding
--disable-background-networking
--no-first-run
--no-default-browser-check
--memory-pressure-off
--single-process
--aggressive-cache-discard
--max_old_space_size=64"

# Start Chrome with low priority
nice -n 15 chromium-browser $CHROME_FLAGS "http://localhost:$DASHBOARD_PORT" &
CHROME_PID=$!
echo "Chrome started with PID: $CHROME_PID"

# Monitor and maintain efficiency
while kill -0 $HTTP_PID 2>/dev/null && kill -0 $CHROME_PID 2>/dev/null; do
    # Check CPU temperature
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
        TEMP_C=$((TEMP / 1000))
        
        if [ "$TEMP_C" -gt 65 ]; then
            echo "High temperature detected ($TEMP_C°C), reducing Chrome priority"
            renice 19 $CHROME_PID >/dev/null 2>&1 || true
        fi
    fi
    
    sleep 10
done

echo "Dashboard processes ended"