#!/bin/bash
# Test Safe Keyboard Toggle
# This script tests the keyboard toggle without interfering with sensor data

echo "🐢 Testing Safe Keyboard Toggle..."
echo "This version should NOT interfere with sensor data input"

# Kill any existing keyboard processes first
echo "Cleaning up any existing keyboards..."
pkill -f onboard 2>/dev/null || true
sleep 1

# Test the safe keyboard toggle
echo "Starting safe keyboard toggle..."
cd /home/shrimp/turtle-monitor/kiosk
python3 safe-keyboard-toggle.py &

# Give it a moment to start
sleep 2

echo "✅ Safe keyboard toggle started"
echo "Click the ⌨️ button in the bottom-right corner to test"
echo "Press Ctrl+C to stop the test"

# Wait for user to test
wait 