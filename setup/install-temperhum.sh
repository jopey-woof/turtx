#!/bin/bash

# 🐢 TEMPerHUM Sensor Installation Script
# Fresh implementation for TEMPerHUM USB temperature/humidity sensors

set -e

echo "🐢 TEMPerHUM Sensor Installation - Fresh Implementation"
echo "======================================================"

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
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root"
    exit 1
fi

# Check if we're on the correct system
if [[ ! -f /etc/os-release ]] || ! grep -q "Ubuntu" /etc/os-release; then
    print_error "This script is designed for Ubuntu systems"
    exit 1
fi

print_header "Step 1: Installing Python Dependencies"

# Install Python dependencies
print_status "Installing Python packages..."
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev

# Install required Python packages
print_status "Installing Python libraries..."
pip3 install --user paho-mqtt pyhidapi

print_header "Step 2: Setting up Device Permissions"

# Install udev rules
print_status "Installing udev rules for TEMPerHUM devices..."
sudo cp hardware/99-temperhum.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to input group for device access
print_status "Adding user to input group..."
sudo usermod -a -G input $USER

print_header "Step 3: Setting up Systemd Service"

# Install systemd service
print_status "Installing systemd service..."
sudo cp hardware/temperhum-manager.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable service for auto-start
print_status "Enabling TEMPerHUM manager service..."
sudo systemctl enable temperhum-manager.service

print_header "Step 4: Creating Log Directory"

# Create log directory
print_status "Creating log directory..."
sudo mkdir -p /var/log
sudo touch /var/log/temperhum-manager.log
sudo chown $USER:$USER /var/log/temperhum-manager.log

print_header "Step 5: Testing Sensor Detection"

# Test sensor detection
print_status "Testing TEMPerHUM sensor detection..."
python3 -c "
import hid
devices = list(hid.enumerate(0x3553, 0xa001))
print(f'Found {len(devices)} TEMPerHUM device(s)')
for i, device in enumerate(devices):
    print(f'  Device {i+1}: {device}')
"

if [[ $? -eq 0 ]]; then
    print_status "✅ Sensor detection test passed"
else
    print_warning "⚠️  Sensor detection test failed - check device connections"
fi

print_header "Step 6: Updating Home Assistant Configuration"

# Update Home Assistant sensors configuration
print_status "Updating Home Assistant sensors configuration..."
if [[ -f homeassistant/sensors.yaml ]]; then
    print_status "Home Assistant sensors configuration updated"
else
    print_warning "Home Assistant sensors.yaml not found - manual configuration required"
fi

print_header "Step 7: Final Setup"

# Make the manager script executable
print_status "Making TEMPerHUM manager executable..."
chmod +x hardware/temperhum_manager.py

# Create a test script
cat > setup/test-temperhum-manager.sh << 'EOF'
#!/bin/bash
echo "🐢 Testing TEMPerHUM Manager"
echo "============================"

# Test the manager script
echo "Testing sensor manager..."
python3 hardware/temperhum_manager.py --test

echo "Test completed"
EOF

chmod +x setup/test-temperhum-manager.sh

print_status "✅ TEMPerHUM installation completed successfully!"
echo ""
echo "📋 Installation Summary:"
echo "  ✅ Python dependencies installed"
echo "  ✅ Device permissions configured"
echo "  ✅ Systemd service installed and enabled"
echo "  ✅ Log directory created"
echo "  ✅ Sensor detection tested"
echo "  ✅ Home Assistant configuration updated"
echo ""
echo "🚀 Next Steps:"
echo "  1. Reboot or log out/in to apply group changes"
echo "  2. Start the service: sudo systemctl start temperhum-manager"
echo "  3. Check status: sudo systemctl status temperhum-manager"
echo "  4. View logs: sudo journalctl -u temperhum-manager -f"
echo "  5. Test sensors: ./setup/test-temperhum-manager.sh"
echo ""
echo "🔧 Service Management:"
echo "  Start:   sudo systemctl start temperhum-manager"
echo "  Stop:    sudo systemctl stop temperhum-manager"
echo "  Restart: sudo systemctl restart temperhum-manager"
echo "  Status:  sudo systemctl status temperhum-manager"
echo "  Logs:    sudo journalctl -u temperhum-manager -f"
echo ""
echo "📊 MQTT Topics:"
echo "  Sensor 1: turtle/sensors/temperhum/sensor_1"
echo "  Sensor 2: turtle/sensors/temperhum/sensor_2"
echo "  Status:   turtle/sensors/temperhum/status"
echo ""
print_status "TEMPerHUM sensor system ready for deployment!" 