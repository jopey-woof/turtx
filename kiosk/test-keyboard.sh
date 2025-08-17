#!/bin/bash

echo "Testing keyboard functionality..."

# Test 1: Can we start onboard manually?
echo "Test 1: Starting onboard manually..."
DISPLAY=:0 onboard --layout=Compact --theme=Nightshade --size=700x250 &
ONBOARD_PID=$!
sleep 3

# Check if onboard is running
if pgrep onboard > /dev/null; then
    echo "✅ Onboard can start manually"
    kill $ONBOARD_PID 2>/dev/null
else
    echo "❌ Onboard failed to start"
fi

# Test 2: Check if wmctrl can find windows
echo "Test 2: Checking window management..."
DISPLAY=:0 wmctrl -l | head -3

echo "Test complete."
