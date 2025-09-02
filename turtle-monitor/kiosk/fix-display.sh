#!/bin/bash

# Fix Display Configuration for TurtX Kiosk
# Eliminates black bars and cursor issues by ensuring single display setup

echo "🖥️ Fixing display configuration..."

# Ensure DISPLAY is set
export DISPLAY=:0

# Force HDMI-1 off and HDMI-2 as primary only
echo "Disabling HDMI-1..."
xrandr --output HDMI-1 --off || true
sleep 1

echo "Configuring HDMI-2 as primary..."
xrandr --output HDMI-2 --primary --mode 1024x600 --pos 0x0 || true
sleep 1

# Verify configuration
echo "Current display configuration:"
xrandr | grep -E "(Screen|connected|primary)"

echo "✅ Display configuration fixed!"