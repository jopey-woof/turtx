#!/bin/bash

# Turtle Monitoring System - Bootstrap Setup
# Phase 1: Basic Kiosk + Home Assistant Foundation
# Run this on the remote machine: ssh shrimp@10.0.20.69 'cd turtle-monitor && ./setup/bootstrap.sh'

set -e

echo "🐢 Turtle Monitoring System - Bootstrap Setup"
echo "=============================================="
echo "Phase 1: Basic Kiosk + Home Assistant Foundation"
echo ""

# Check if running on correct machine
if [ "$USER" != "shrimp" ]; then
    echo "❌ Error: This script should be run as user 'shrimp' on the remote machine"
    echo "   Please run: ssh shrimp@10.0.20.69 'cd turtle-monitor && ./setup/bootstrap.sh'"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "setup/bootstrap.sh" ]; then
    echo "❌ Error: Please run this script from the turtle-monitor directory"
    echo "   cd /home/shrimp/turtle-monitor && ./setup/bootstrap.sh"
    exit 1
fi

echo "📋 System Information:"
echo "- User: $USER"
echo "- Hostname: $(hostname)"
echo "- OS: $(lsb_release -d | cut -f2)"
echo "- Directory: $(pwd)"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🔍 Checking prerequisites..."

# Check if Docker is installed
if ! command_exists docker; then
    echo "📦 Installing Docker..."
    ./setup/install-docker.sh
else
    echo "✅ Docker is already installed"
    docker --version
fi

# Check if Docker Compose is installed
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✅ Docker Compose is already installed"
    if command_exists docker-compose; then
        docker-compose --version
    else
        docker compose version
    fi
fi

echo ""
echo "🔐 Setting up secrets..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please run the secrets setup first:"
    echo "   ./setup/setup-secrets.sh"
    echo ""
    echo "This will prompt you for all required passwords and configuration."
    exit 1
else
    echo "✅ .env file found"
fi

# Load environment variables
set -a
source .env
set +a

echo ""
echo "🖥️  Setting up display system..."

# Update package list
sudo apt update

# Install basic desktop environment and X11 (minimal for kiosk)
echo "Installing minimal desktop environment..."
sudo apt install -y \
    xorg \
    xinit \
    openbox \
    chromium-browser \
    unclutter \
    x11vnc \
    autocutsel

# Install touchscreen support
echo "Installing touchscreen drivers..."
sudo apt install -y \
    xserver-xorg-input-evdev \
    xserver-xorg-input-libinput \
    xinput-calibrator

echo ""
echo "🏠 Setting up Home Assistant..."

# Create Home Assistant directory structure
mkdir -p homeassistant/.storage
mkdir -p docker/data

# Set proper permissions
sudo chown -R $USER:$USER homeassistant/
sudo chown -R $USER:$USER docker/

echo "Starting Home Assistant container..."
cd docker
docker-compose pull
docker-compose up -d homeassistant

echo "Waiting for Home Assistant to start..."
sleep 30

# Check if Home Assistant is running
if docker-compose ps homeassistant | grep -q "Up"; then
    echo "✅ Home Assistant is running"
else
    echo "⚠️  Home Assistant may still be starting. Check logs with:"
    echo "   cd docker && docker-compose logs homeassistant"
fi

cd ..

echo ""
echo "🖼️  Setting up kiosk mode..."

# Create kiosk startup script
./setup/install-display.sh

echo ""
echo "🔧 Setting up system services..."

# Copy kiosk service file to systemd
sudo cp kiosk/kiosk.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable kiosk service (don't start yet)
sudo systemctl enable kiosk.service

echo ""
echo "✅ Phase 1 Bootstrap Complete!"
echo ""
echo "🎯 What's been set up:"
echo "- ✅ Docker and Docker Compose"
echo "- ✅ Minimal desktop environment (Openbox)"
echo "- ✅ Chromium browser for kiosk mode" 
echo "- ✅ Home Assistant container running"
echo "- ✅ Touchscreen drivers installed"
echo "- ✅ Kiosk service configured (not started)"
echo ""
echo "🔍 Next steps for Phase 1 validation:"
echo "1. Test Home Assistant access:"
echo "   curl http://localhost:8123"
echo ""
echo "2. Test X11 display (run from SSH with X forwarding):"
echo "   export DISPLAY=:0"
echo "   startx /usr/bin/openbox-session"
echo ""
echo "3. Test kiosk mode:"
echo "   sudo systemctl start kiosk.service"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status kiosk.service"
echo ""
echo "5. View Home Assistant logs:"
echo "   cd docker && docker-compose logs homeassistant"
echo ""
echo "🐢 Phase 1 Foundation Ready!"
echo "Once you validate these components work, we can proceed to Phase 2 (hardware integration)."
echo ""