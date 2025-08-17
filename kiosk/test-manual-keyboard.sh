#!/bin/bash

echo "=== Manual Keyboard Test ==="
echo "Testing onboard visibility over Chrome kiosk..."

# Set display
export DISPLAY=:0

echo "1. Starting onboard manually..."
onboard --layout=Compact --theme=Nightshade --size=600x180 --xid &
ONBOARD_PID=$!

sleep 4

echo "2. Checking if onboard window exists..."
wmctrl -l | grep -i onboard

echo "3. Attempting to position onboard..."
wmctrl -r "Onboard" -e 0,50,350,600,180
sleep 1
wmctrl -r "Onboard" -b add,above,skip_taskbar
sleep 1
wmctrl -r "Onboard" -a

echo "4. Final window list:"
wmctrl -l

echo "5. Onboard should now be visible at coordinates 50,350"
echo "Press Enter to kill onboard..."
read

kill $ONBOARD_PID 2>/dev/null
echo "Test complete."
