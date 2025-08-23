#!/bin/bash

echo "=== Testing keyboard positioning ==="

# Start onboard manually with same settings
echo "Starting onboard manually..."
DISPLAY=:0 onboard --layout=Compact --theme=Nightshade --size=650x220 &
ONBOARD_PID=$!

sleep 3

echo "Current onboard windows:"
DISPLAY=:0 wmctrl -l | grep -i onboard

echo "Applying positioning..."
DISPLAY=:0 wmctrl -r "Onboard" -e 0,10,380,650,220
DISPLAY=:0 wmctrl -r "Onboard" -b add,above
DISPLAY=:0 wmctrl -r "Onboard" -b add,sticky

sleep 2

echo "Window positions after commands:"
DISPLAY=:0 wmctrl -l | grep -i onboard

echo "Keyboard should now be visible at bottom left corner!"
echo "Press Enter to close test keyboard..."
read

kill $ONBOARD_PID 2>/dev/null
echo "Test complete."
