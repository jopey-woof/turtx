#!/bin/bash

# Permanent Display Configuration for TurtX Kiosk
# Ensures only HDMI-2 (touchscreen) is active to prevent black bars

echo "🖥️ Setting permanent display configuration..."

# Ensure DISPLAY is set
export DISPLAY=:0

# Always disable HDMI-1 and enable only HDMI-2
echo "Disabling HDMI-1 permanently..."
xrandr --output HDMI-1 --off || true

echo "Configuring HDMI-2 as primary..."
xrandr --output HDMI-2 --primary --mode 1024x600 --pos 0x0 --rotate normal || true

# Disable power management to prevent display issues
xset -dpms || true
xset s off || true
xset s noblank || true

# Set optimal display settings
xrandr --output HDMI-2 --brightness 0.9 || true

echo "✅ Display configuration applied"

# Verify configuration
echo "Current display status:"
xrandr | grep -E "(Screen|connected)" | head -3