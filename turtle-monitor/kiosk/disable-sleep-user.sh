#!/bin/bash

# Turtle Monitor - Disable Sleep and Screen Saver (User Level)
# This script prevents the kiosk from going to sleep or showing screen saver

echo "🐢 Disabling sleep and screen saver for Turtle Monitor Kiosk..."

export DISPLAY=:0

# Disable GNOME screen saver
echo "📺 Disabling GNOME screen saver..."
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false 2>/dev/null || true
gsettings set org.gnome.desktop.session idle-delay 0 2>/dev/null || true

# Disable X11 screen saver and power management
echo "⚡ Disabling X11 power management..."
xset s off 2>/dev/null || true
xset s noblank 2>/dev/null || true
xset -dpms 2>/dev/null || true

# Create a keep-alive script that runs periodically
echo "🔄 Creating keep-alive mechanism..."
cat > /home/shrimp/turtx/turtle-monitor/kiosk/kiosk-keep-alive.sh << 'EOF'
#!/bin/bash
# Keep the kiosk awake by simulating activity

export DISPLAY=:0

while true; do
    # Move mouse slightly to prevent sleep (invisible to user)
    xdotool mousemove_relative 1 0 2>/dev/null || true
    xdotool mousemove_relative -1 0 2>/dev/null || true
    
    # Re-apply X11 settings
    xset s off 2>/dev/null || true
    xset s noblank 2>/dev/null || true
    xset -dpms 2>/dev/null || true
    
    # Wait 5 minutes before next check
    sleep 300
done
EOF

chmod +x /home/shrimp/turtx/turtle-monitor/kiosk/kiosk-keep-alive.sh

# Kill any existing keep-alive processes
pkill -f "kiosk-keep-alive.sh" 2>/dev/null || true

# Start keep-alive in background
echo "🚀 Starting keep-alive service..."
nohup /home/shrimp/turtx/turtle-monitor/kiosk/kiosk-keep-alive.sh > /tmp/kiosk-keep-alive.log 2>&1 &

echo "✅ Sleep and screen saver disabled for Turtle Monitor Kiosk!"
echo "📊 Kiosk will stay awake indefinitely"
echo "🔄 Keep-alive service running in background"
echo "📝 Log file: /tmp/kiosk-keep-alive.log" 