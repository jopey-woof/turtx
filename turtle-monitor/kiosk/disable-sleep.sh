#!/bin/bash

# Turtle Monitor - Disable Sleep and Screen Saver
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

# Disable system sleep
echo "💤 Disabling system sleep..."
systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target 2>/dev/null || true

# Set power management to never sleep
echo "🔋 Configuring power management..."
if command -v xfce4-power-manager >/dev/null 2>&1; then
    xfce4-power-manager --no-daemon --disable-timer 2>/dev/null || true
fi

# Disable automatic suspend
if command -v systemctl >/dev/null 2>&1; then
    systemctl disable systemd-suspend.service 2>/dev/null || true
    systemctl mask systemd-suspend.service 2>/dev/null || true
fi

# Create a keep-alive script that runs periodically
echo "🔄 Creating keep-alive mechanism..."
cat > /usr/local/bin/kiosk-keep-alive.sh << 'EOF'
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

chmod +x /usr/local/bin/kiosk-keep-alive.sh

# Start keep-alive in background
echo "🚀 Starting keep-alive service..."
nohup /usr/local/bin/kiosk-keep-alive.sh > /tmp/kiosk-keep-alive.log 2>&1 &

echo "✅ Sleep and screen saver disabled for Turtle Monitor Kiosk!"
echo "📊 Kiosk will stay awake indefinitely"
echo "🔄 Keep-alive service running in background" 