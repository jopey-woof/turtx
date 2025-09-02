#!/bin/bash

# TurtX Permanent Boot Configuration
# Ensures correct display and optimizations persist across reboots

echo "🔧 Applying permanent TurtX optimizations..."

# Make display configuration script available at boot
sudo cp /home/shrimp/turtx/turtle-monitor/kiosk/display-config.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/display-config.sh

# Create boot-time display fix
sudo tee /etc/systemd/system/turtx-display-fix.service > /dev/null << 'EOF'
[Unit]
Description=TurtX Display Configuration Fix
After=graphical.target
Wants=graphical.target

[Service]
Type=oneshot
User=shrimp
Group=shrimp
Environment=DISPLAY=:0
ExecStart=/usr/local/bin/display-config.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOF

# Enable the service
sudo systemctl enable turtx-display-fix.service

# Create CPU optimization service
sudo tee /etc/systemd/system/turtx-cpu-optimize.service > /dev/null << 'EOF'
[Unit]
Description=TurtX CPU Optimization
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo 10 > /proc/sys/vm/swappiness'
ExecStart=/bin/bash -c 'echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo || true'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# Enable CPU optimization
sudo systemctl enable turtx-cpu-optimize.service

echo "✅ Permanent optimizations configured!"
echo "These will now apply automatically on every boot."