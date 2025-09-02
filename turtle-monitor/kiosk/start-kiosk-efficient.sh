#!/bin/bash

# TurtX Efficient Kiosk Startup Script
# Designed for minimal resource usage to prevent fan overload

set -e

echo "🐢 Starting TurtX Kiosk in Efficient Mode..."

# Kill any existing Chrome processes
pkill -f chrome || true
pkill -f chromium || true
sleep 2

# Set CPU governor to powersave to reduce heat
echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1 || true

# Disable hardware acceleration and limit Chrome processes
export DISPLAY=:0
export CHROME_FLAGS="
--kiosk
--no-sandbox
--disable-web-security
--disable-features=TranslateUI,VizDisplayCompositor
--disable-ipc-flooding-protection
--disable-renderer-backgrounding
--disable-backgrounding-occluded-windows
--disable-background-timer-throttling
--disable-background-networking
--disable-back-forward-cache
--disable-breakpad
--disable-component-extensions-with-background-pages
--disable-extensions
--disable-features=TranslateUI
--disable-hang-monitor
--disable-ipc-flooding-protection
--disable-popup-blocking
--disable-prompt-on-repost
--disable-renderer-backgrounding
--disable-sync
--disable-translate
--disable-background-timer-throttling
--no-first-run
--no-default-browser-check
--no-pings
--password-store=basic
--use-mock-keychain
--disable-gpu
--disable-software-rasterizer
--disable-dev-shm-usage
--memory-pressure-off
--max_old_space_size=128
--process-per-site
--single-process
--disable-site-isolation-trials
--aggressive-cache-discard
--memory-pressure-off
--max-old-space-size=64"

# Set nice priority to reduce CPU usage
nice -n 10 chromium-browser $CHROME_FLAGS "http://localhost:8080" &

CHROME_PID=$!
echo "Chrome started with PID: $CHROME_PID"

# Monitor and limit Chrome CPU usage
(
    while kill -0 $CHROME_PID 2>/dev/null; do
        # Get Chrome CPU usage
        CPU_USAGE=$(ps -p $CHROME_PID -o %cpu= 2>/dev/null | tr -d ' ' || echo "0")
        
        # If CPU usage is too high, lower priority further
        if (( $(echo "$CPU_USAGE > 30" | bc -l 2>/dev/null || echo "0") )); then
            renice 15 $CHROME_PID >/dev/null 2>&1 || true
            echo "High CPU detected ($CPU_USAGE%), reducing Chrome priority"
        fi
        
        sleep 5
    done
) &

# Wait for Chrome process
wait $CHROME_PID