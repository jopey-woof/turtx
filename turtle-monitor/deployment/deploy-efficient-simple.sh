#!/bin/bash

# TurtX Simple Efficient Kiosk Deployment
# Handles sudo authentication and deploys lightweight dashboard

set -e

REMOTE_HOST="shrimp@10.0.20.69"
PROJECT_DIR="/home/shrimp/turtle-monitor"

echo "🐢 Deploying TurtX Efficient Kiosk Dashboard..."

# Copy files first
echo "📁 Creating directories and copying files..."
ssh $REMOTE_HOST "mkdir -p $PROJECT_DIR/{frontend,kiosk,config,logs}"

scp frontend/index.html $REMOTE_HOST:$PROJECT_DIR/frontend/
scp frontend/camera.html $REMOTE_HOST:$PROJECT_DIR/frontend/
scp frontend/data.html $REMOTE_HOST:$PROJECT_DIR/frontend/
scp kiosk/start-kiosk-efficient.sh $REMOTE_HOST:$PROJECT_DIR/kiosk/
scp kiosk/turtx-kiosk.service $REMOTE_HOST:$PROJECT_DIR/kiosk/
scp kiosk/monitor-system-efficiency.sh $REMOTE_HOST:$PROJECT_DIR/kiosk/
scp config/nginx-efficient.conf $REMOTE_HOST:$PROJECT_DIR/config/

echo "🔧 Setting up permissions and services..."
ssh $REMOTE_HOST "
chmod +x $PROJECT_DIR/kiosk/*.sh

# Setup nginx with password
echo 'shrimp' | sudo -S cp $PROJECT_DIR/config/nginx-efficient.conf /etc/nginx/sites-available/turtx-kiosk
echo 'shrimp' | sudo -S ln -sf /etc/nginx/sites-available/turtx-kiosk /etc/nginx/sites-enabled/
echo 'shrimp' | sudo -S nginx -t && echo 'shrimp' | sudo -S systemctl reload nginx

# Setup systemd service
echo 'shrimp' | sudo -S cp $PROJECT_DIR/kiosk/turtx-kiosk.service /etc/systemd/system/
echo 'shrimp' | sudo -S systemctl daemon-reload

# Stop any existing kiosk services
echo 'shrimp' | sudo -S systemctl stop kiosk.service 2>/dev/null || true
echo 'shrimp' | sudo -S systemctl stop turtle-monitor-kiosk.service 2>/dev/null || true

# Optimize system for efficiency
echo 'shrimp' | sudo -S bash -c 'echo powersave > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor' 2>/dev/null || true

# Kill any existing Chrome processes
pkill -f chrome || true
pkill -f chromium || true
sleep 2

# Start the efficient kiosk
echo 'shrimp' | sudo -S systemctl enable turtx-kiosk.service
echo 'shrimp' | sudo -S systemctl start turtx-kiosk.service
"

echo "✅ Deployment complete!"
echo ""
echo "📊 Checking service status..."
ssh $REMOTE_HOST "sudo systemctl status turtx-kiosk.service --no-pager -l | head -20"

echo ""
echo "🌐 Dashboard available at: http://10.0.20.69:8080"
echo "📝 Monitor logs: ssh $REMOTE_HOST 'journalctl -u turtx-kiosk.service -f'"