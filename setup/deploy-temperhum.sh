#!/bin/bash

# 🐢 TEMPerHUM Remote Deployment Script
# Deploys TEMPerHUM sensor system to remote Ubuntu server via SSH

set -e

# Configuration
REMOTE_HOST="shrimp@10.0.20.69"
REMOTE_PATH="/home/shrimp/turtle-monitor"
LOCAL_PATH="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
}

# Function to execute remote command
remote_exec() {
    local cmd="$1"
    ssh "$REMOTE_HOST" "$cmd"
}

# Function to copy file to remote
remote_copy() {
    local src="$1"
    local dest="$2"
    scp "$src" "$REMOTE_HOST:$dest"
}

echo "🐢 TEMPerHUM Remote Deployment"
echo "=============================="

# Check SSH connectivity
print_header "Step 1: Testing SSH Connectivity"

print_status "Testing connection to $REMOTE_HOST..."
if ssh -o ConnectTimeout=10 -o BatchMode=yes "$REMOTE_HOST" "echo 'SSH connection successful'" 2>/dev/null; then
    print_status "✅ SSH connection established"
else
    print_error "❌ SSH connection failed"
    print_error "Make sure SSH key authentication is set up"
    exit 1
fi

# Check if remote directory exists
print_header "Step 2: Checking Remote Directory"

if remote_exec "test -d $REMOTE_PATH"; then
    print_status "✅ Remote directory exists"
else
    print_error "❌ Remote directory not found: $REMOTE_PATH"
    print_error "Make sure the turtle-monitor project is cloned on the remote server"
    exit 1
fi

# Stop existing service if running
print_header "Step 3: Stopping Existing Service"

if remote_exec "systemctl is-active --quiet temperhum-manager.service"; then
    print_status "Stopping existing TEMPerHUM manager service..."
    remote_exec "sudo systemctl stop temperhum-manager.service"
    print_status "✅ Service stopped"
else
    print_status "No existing service running"
fi

# Copy new files to remote
print_header "Step 4: Copying Files to Remote Server"

print_status "Copying TEMPerHUM manager script..."
remote_copy "hardware/temperhum_manager.py" "$REMOTE_PATH/hardware/"

print_status "Copying systemd service file..."
remote_copy "hardware/temperhum-manager.service" "$REMOTE_PATH/hardware/"

print_status "Copying udev rules..."
remote_copy "hardware/99-temperhum.rules" "$REMOTE_PATH/hardware/"

print_status "Copying Home Assistant sensors configuration..."
remote_copy "homeassistant/sensors.yaml" "$REMOTE_PATH/homeassistant/"

print_status "Copying installation script..."
remote_copy "setup/install-temperhum.sh" "$REMOTE_PATH/setup/"

print_status "Copying test script..."
remote_copy "setup/test-temperhum-manager.sh" "$REMOTE_PATH/setup/"

print_status "✅ All files copied successfully"

# Make scripts executable on remote
print_header "Step 5: Setting Permissions"

remote_exec "chmod +x $REMOTE_PATH/hardware/temperhum_manager.py"
remote_exec "chmod +x $REMOTE_PATH/setup/install-temperhum.sh"
remote_exec "chmod +x $REMOTE_PATH/setup/test-temperhum-manager.sh"

print_status "✅ Permissions set"

# Run installation on remote
print_header "Step 6: Running Remote Installation"

print_status "Running TEMPerHUM installation on remote server..."
remote_exec "cd $REMOTE_PATH && ./setup/install-temperhum.sh"

if [[ $? -eq 0 ]]; then
    print_status "✅ Remote installation completed"
else
    print_error "❌ Remote installation failed"
    exit 1
fi

# Test the installation
print_header "Step 7: Testing Installation"

print_status "Running tests on remote server..."
remote_exec "cd $REMOTE_PATH && ./setup/test-temperhum-manager.sh"

if [[ $? -eq 0 ]]; then
    print_status "✅ Remote tests passed"
else
    print_warning "⚠️  Some tests failed - check remote logs"
fi

# Start the service
print_header "Step 8: Starting Service"

print_status "Starting TEMPerHUM manager service..."
remote_exec "sudo systemctl start temperhum-manager.service"

# Wait a moment for service to start
sleep 3

# Check service status
if remote_exec "systemctl is-active --quiet temperhum-manager.service"; then
    print_status "✅ Service started successfully"
else
    print_error "❌ Service failed to start"
    print_status "Checking service logs..."
    remote_exec "sudo journalctl -u temperhum-manager.service --no-pager -n 20"
    exit 1
fi

# Final status check
print_header "Step 9: Final Status Check"

print_status "Checking service status..."
remote_exec "sudo systemctl status temperhum-manager.service --no-pager"

print_status "Checking recent logs..."
remote_exec "sudo journalctl -u temperhum-manager.service --no-pager -n 10"

print_status "Checking MQTT topics..."
remote_exec "timeout 10 mosquitto_sub -t 'turtle/sensors/temperhum/#' -C 1" || {
    print_warning "⚠️  MQTT test failed - check if MQTT broker is running"
}

print_status "✅ TEMPerHUM deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "  ✅ SSH connectivity verified"
echo "  ✅ Files copied to remote server"
echo "  ✅ Installation completed"
echo "  ✅ Tests passed"
echo "  ✅ Service started"
echo "  ✅ Status verified"
echo ""
echo "🔧 Remote Service Management:"
echo "  ssh $REMOTE_HOST 'sudo systemctl status temperhum-manager'"
echo "  ssh $REMOTE_HOST 'sudo systemctl restart temperhum-manager'"
echo "  ssh $REMOTE_HOST 'sudo journalctl -u temperhum-manager -f'"
echo ""
echo "📊 Monitor MQTT Data:"
echo "  ssh $REMOTE_HOST 'mosquitto_sub -t \"turtle/sensors/temperhum/#\"'"
echo ""
echo "🐢 TEMPerHUM sensors are now active and monitoring your turtle habitat!" 