#!/bin/bash

# TurtX Professional Kiosk Startup
# Optimized for performance and reliability

set -e

echo "🐢 Starting TurtX Professional Kiosk Dashboard..."

# Kill existing processes
pkill -f 'python.*8090' || true
pkill -f firefox || true
pkill -f chromium || true
sleep 3

# Set CPU governor to powersave for efficiency
echo 'shrimp' | sudo -S bash -c 'echo powersave > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor' 2>/dev/null || true

# Start HTTP server
cd /home/shrimp/turtle-monitor/frontend
python3 -m http.server 8090 --bind 0.0.0.0 > /dev/null 2>&1 &
HTTP_PID=$!
echo "✅ HTTP server started (PID: $HTTP_PID)"

# Wait for server to start
sleep 3

# Test server
if curl -s http://localhost:8090 > /dev/null; then
    echo "✅ Dashboard accessible at http://localhost:8090"
else
    echo "❌ Dashboard not accessible"
    exit 1
fi

# Start Firefox kiosk
export DISPLAY=:0
nohup nice -n 10 firefox \
    --kiosk \
    --private-window \
    'http://localhost:8090' > /dev/null 2>&1 &

FIREFOX_PID=$!
echo "✅ Firefox kiosk started (PID: $FIREFOX_PID)"

echo ""
echo "🎯 TurtX Professional Dashboard Status:"
echo "   📊 Dashboard: http://10.0.20.69:8090"
echo "   🖥️  Kiosk: Running on display :0"
echo "   🔧 CPU: Set to powersave mode"
echo "   📡 API: http://10.0.20.69/api/latest"
echo ""
echo "✨ Professional monitoring system is now active!"