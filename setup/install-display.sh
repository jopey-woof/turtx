#!/bin/bash

# Turtle Monitoring System - Display & Kiosk Setup
# Configure X11, touchscreen, and kiosk mode for turtle monitoring

set -e

echo "🖥️  Setting up display and kiosk configuration..."

# Load environment variables if available
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

# Set defaults if not in .env
DISPLAY_RESOLUTION=${DISPLAY_RESOLUTION:-1024x600}
CHROMIUM_FLAGS=${CHROMIUM_FLAGS:-"--kiosk --disable-features=VizDisplayCompositor --disable-backgrounding-occluded-windows"}

echo "📺 Display resolution: $DISPLAY_RESOLUTION"

# Create kiosk startup script
echo "Creating kiosk startup script..."
cat > kiosk/start-kiosk.sh << 'EOF'
#!/bin/bash

# Turtle Kiosk Startup Script
# Starts X11 with Chromium in kiosk mode displaying Home Assistant

set -e

# Load environment variables
if [ -f "/home/shrimp/turtle-monitor/.env" ]; then
    set -a
    source /home/shrimp/turtle-monitor/.env
    set +a
fi

export DISPLAY=:0
export HOME=/home/shrimp

# Kill any existing X processes
pkill -f "xinit\|Xorg\|chromium" || true
sleep 2

# Set up X11 environment
export XAUTHORITY=/home/shrimp/.Xauthority

# Configure touchscreen
echo "Configuring touchscreen..."
xinput --set-prop "$(xinput list --name-only | grep -i touch | head -1)" "Coordinate Transformation Matrix" 1 0 0 0 1 0 0 0 1 2>/dev/null || true

# Hide cursor after 1 second of inactivity
unclutter -idle 1 -root &

# Start clipboard manager
autocutsel -fork &

# Wait for Home Assistant to be available
echo "Waiting for Home Assistant..."
while ! curl -s http://localhost:8123 > /dev/null; do
    sleep 5
done

# Start Chromium in kiosk mode
echo "Starting Chromium kiosk mode..."
chromium-browser \
    --kiosk \
    --disable-features=VizDisplayCompositor \
    --disable-backgrounding-occluded-windows \
    --disable-background-timer-throttling \
    --disable-renderer-backgrounding \
    --disable-field-trial-config \
    --disable-web-security \
    --disable-features=TranslateUI \
    --disable-ipc-flooding-protection \
    --no-first-run \
    --fast \
    --fast-start \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-translate \
    --window-size=${DISPLAY_RESOLUTION/x/,} \
    --window-position=0,0 \
    --start-fullscreen \
    "http://localhost:8123"

EOF

chmod +x kiosk/start-kiosk.sh

# Create X11 configuration for auto-login and display
echo "Creating X11 configuration..."
cat > kiosk/xinit-kiosk << 'EOF'
#!/bin/bash

# X11 startup for turtle kiosk
export DISPLAY=:0

# Start window manager
openbox-session &

# Wait for window manager
sleep 2

# Start kiosk
/home/shrimp/turtle-monitor/kiosk/start-kiosk.sh

EOF

chmod +x kiosk/xinit-kiosk

# Create systemd service for kiosk
echo "Creating systemd service..."
cat > kiosk/kiosk.service << 'EOF'
[Unit]
Description=Turtle Monitoring Kiosk Display
After=docker.service
Wants=docker.service
After=graphical.target
Wants=graphical.target

[Service]
Type=simple
User=shrimp
Group=shrimp
WorkingDirectory=/home/shrimp/turtle-monitor
Environment=DISPLAY=:0
Environment=HOME=/home/shrimp
Environment=XDG_RUNTIME_DIR=/run/user/1000
ExecStartPre=/bin/bash -c 'while ! docker ps | grep -q homeassistant; do sleep 5; done'
ExecStart=/usr/bin/xinit /home/shrimp/turtle-monitor/kiosk/xinit-kiosk -- :0 vt7
Restart=always
RestartSec=5
StartLimitIntervalSec=0

[Install]
WantedBy=multi-user.target
EOF

# Set up auto-login for user shrimp
echo "Configuring auto-login..."
echo "shrimp" | sudo -S mkdir -p /etc/systemd/system/getty@tty1.service.d/
echo "shrimp" | sudo -S tee /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null << 'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --noissue --autologin shrimp %I $TERM
Type=idle
EOF

# Create .xinitrc for user
echo "Creating .xinitrc..."
cat > /home/shrimp/.xinitrc << 'EOF'
#!/bin/bash

# Start the kiosk interface
exec /home/shrimp/turtle-monitor/kiosk/xinit-kiosk
EOF

chmod +x /home/shrimp/.xinitrc

# Configure X11 to allow any user to start X (for kiosk)
echo "Configuring X11 permissions..."
echo "shrimp" | sudo -S tee /etc/X11/Xwrapper.config > /dev/null << 'EOF'
allowed_users=anybody
needs_root_rights=yes
EOF

# Create touchscreen calibration if device exists
if [ -e /dev/input/event* ]; then
    echo "Setting up basic touchscreen configuration..."
    # This will be refined once we test with actual hardware
    echo "shrimp" | sudo -S tee /usr/share/X11/xorg.conf.d/40-libinput.conf > /dev/null << 'EOF'
Section "InputClass"
    Identifier "libinput touchscreen catchall"
    MatchIsTouchscreen "on"
    MatchDevicePath "/dev/input/event*"
    Driver "libinput"
EndSection
EOF
fi

echo "✅ Display and kiosk setup complete!"
echo ""
echo "📝 Configuration summary:"
echo "- Auto-login configured for user 'shrimp'"
echo "- Kiosk service created (not started yet)"
echo "- Chromium configured for touchscreen kiosk mode"
echo "- X11 configured for direct hardware access"
echo "- Touchscreen drivers configured"
echo ""
echo "🧪 To test the kiosk setup:"
echo "1. echo "shrimp" | sudo -S systemctl start kiosk.service"
echo "2. Check status: echo "shrimp" | sudo -S systemctl status kiosk.service"
echo "3. View logs: echo "shrimp" | sudo -S journalctl -u kiosk.service -f"
echo ""