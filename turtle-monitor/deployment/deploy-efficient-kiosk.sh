#!/bin/bash

# TurtX Efficient Kiosk Deployment Script
# Designed to prevent fan overload and maintain professional standards

set -e

REMOTE_HOST="shrimp@10.0.20.69"
PROJECT_DIR="/home/shrimp/turtle-monitor"

echo "🐢 Deploying TurtX Efficient Kiosk Dashboard..."

# Function to run commands on remote host
run_remote() {
    ssh $REMOTE_HOST "$1"
}

# Function to copy files to remote host
copy_to_remote() {
    scp -r "$1" "$REMOTE_HOST:$2"
}

echo "📁 Creating project directories..."
run_remote "mkdir -p $PROJECT_DIR/{frontend,kiosk,config,logs}"

echo "📄 Copying frontend files..."
copy_to_remote "frontend/index.html" "$PROJECT_DIR/frontend/"

echo "📄 Copying kiosk configuration..."
copy_to_remote "kiosk/start-kiosk-efficient.sh" "$PROJECT_DIR/kiosk/"
copy_to_remote "kiosk/turtx-kiosk.service" "$PROJECT_DIR/kiosk/"

echo "📄 Copying nginx configuration..."
copy_to_remote "config/nginx-efficient.conf" "$PROJECT_DIR/config/"

echo "🔧 Setting up permissions..."
run_remote "chmod +x $PROJECT_DIR/kiosk/start-kiosk-efficient.sh"

echo "🌐 Setting up nginx..."
run_remote "sudo cp $PROJECT_DIR/config/nginx-efficient.conf /etc/nginx/sites-available/turtx-kiosk"
run_remote "sudo ln -sf /etc/nginx/sites-available/turtx-kiosk /etc/nginx/sites-enabled/"
run_remote "sudo nginx -t && sudo systemctl reload nginx"

echo "⚙️ Setting up systemd service..."
run_remote "sudo cp $PROJECT_DIR/kiosk/turtx-kiosk.service /etc/systemd/system/"
run_remote "sudo systemctl daemon-reload"

echo "🔧 Optimizing system for kiosk mode..."
run_remote "
# Set CPU governor to powersave
echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Disable unnecessary services that might cause heat
sudo systemctl disable bluetooth || true
sudo systemctl disable cups || true
sudo systemctl disable avahi-daemon || true

# Set swappiness for better memory management
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# Apply sysctl settings
sudo sysctl -p
"

echo "🚀 Starting TurtX Kiosk service..."
run_remote "sudo systemctl enable turtx-kiosk.service"
run_remote "sudo systemctl start turtx-kiosk.service"

echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
run_remote "sudo systemctl status turtx-kiosk.service --no-pager -l"

echo ""
echo "🌐 Dashboard should be available at: http://10.0.20.69:8080"
echo "📝 To check logs: ssh $REMOTE_HOST 'journalctl -u turtx-kiosk.service -f'"
echo "🔄 To restart: ssh $REMOTE_HOST 'sudo systemctl restart turtx-kiosk.service'"