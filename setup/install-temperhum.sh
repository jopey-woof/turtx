#!/bin/bash
# TemperhUM Sensor Integration Setup Script
# Complete one-click installation for turtle enclosure monitoring

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/shrimp/turtle-monitor"
HARDWARE_DIR="$PROJECT_ROOT/hardware"
SETUP_DIR="$PROJECT_ROOT/setup"
LOG_FILE="/var/log/temperhum-setup.log"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as shrimp user."
    fi
}

# Check system requirements
check_system() {
    log "Checking system requirements..."
    
    # Check Ubuntu version
    if ! grep -q "Ubuntu" /etc/os-release; then
        error "This script is designed for Ubuntu systems"
    fi
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is required but not installed"
    fi
    
    log "System requirements check passed"
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    # Install system packages
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-dev python3-evdev
    
    # Install Python packages
    pip3 install --user paho-mqtt evdev python-evdev
    
    log "Python dependencies installed"
}

# Setup udev rules
setup_udev_rules() {
    log "Setting up udev rules for sensor access..."
    
    # Copy udev rules
    sudo cp "$HARDWARE_DIR/99-temperhum-sensors.rules" /etc/udev/rules.d/
    
    # Set proper permissions
    sudo chmod 644 /etc/udev/rules.d/99-temperhum-sensors.rules
    
    # Reload udev rules
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    log "Udev rules installed and reloaded"
}

# Setup MQTT broker
setup_mqtt() {
    log "Setting up MQTT broker..."
    
    # Check if MQTT broker is already running
    if systemctl is-active --quiet mosquitto; then
        log "MQTT broker (mosquitto) is already running"
        return
    fi
    
    # Install mosquitto
    sudo apt-get install -y mosquitto mosquitto-clients
    
    # Create mosquitto configuration
    sudo tee /etc/mosquitto/conf.d/temperhum.conf > /dev/null <<EOF
# TemperhUM Sensor MQTT Configuration
listener 1883
allow_anonymous true
persistence true
persistence_location /var/lib/mosquitto/
log_dest file /var/log/mosquitto/mosquitto.log
log_dest stdout
log_type all
EOF
    
    # Start and enable mosquitto
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto
    
    log "MQTT broker installed and started"
}

# Setup systemd service
setup_service() {
    log "Setting up systemd service..."
    
    # Copy service file
    sudo cp "$HARDWARE_DIR/temperhum-capture.service" /etc/systemd/system/
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable temperhum-capture.service
    
    log "Systemd service installed and enabled"
}

# Create data directory and files
setup_data_files() {
    log "Setting up data files..."
    
    # Create log directory
    sudo mkdir -p /var/log
    sudo touch /var/log/temperhum-capture.log
    sudo chown shrimp:shrimp /var/log/temperhum-capture.log
    
    # Create data file
    touch /tmp/temperhum_data.txt
    chmod 666 /tmp/temperhum_data.txt
    
    log "Data files created"
}

# Test sensor detection
test_sensor_detection() {
    log "Testing sensor detection..."
    
    # Run sensor detection test
    cd "$HARDWARE_DIR"
    python3 -c "
import evdev
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
keyboard_devices = [d for d in devices if evdev.ecodes.EV_KEY in d.capabilities()]
print(f'Found {len(keyboard_devices)} keyboard devices:')
for device in keyboard_devices:
    print(f'  - {device.name} at {device.path}')
"
    
    log "Sensor detection test completed"
}

# Test data capture
test_data_capture() {
    log "Testing data capture..."
    
    # Create test data
    echo "29.54[C]39.58[%RH]1S" >> /tmp/temperhum_data.txt
    echo "27.60[C]40.38[%RH]2S" >> /tmp/temperhum_data.txt
    
    # Test parsing
    cd "$HARDWARE_DIR"
    python3 -c "
import sys
sys.path.append('.')
from simple_data_capture import SimpleDataCapture
capture = SimpleDataCapture(debug=True)
parsed = capture.parse_sensor_data('29.54[C]39.58[%RH]1S')
print(f'Test parsing result: {parsed}')
"
    
    log "Data capture test completed"
}

# Start the service
start_service() {
    log "Starting TemperhUM capture service..."
    
    sudo systemctl start temperhum-capture.service
    
    # Wait a moment for service to start
    sleep 3
    
    # Check service status
    if systemctl is-active --quiet temperhum-capture.service; then
        log "Service started successfully"
    else
        error "Failed to start service"
    fi
}

# Display status
show_status() {
    log "Displaying system status..."
    
    echo
    echo "=== TemperhUM Sensor Integration Status ==="
    echo
    
    # Service status
    echo "Service Status:"
    systemctl status temperhum-capture.service --no-pager -l || true
    echo
    
    # MQTT status
    echo "MQTT Broker Status:"
    systemctl status mosquitto --no-pager -l || true
    echo
    
    # Recent logs
    echo "Recent Logs:"
    tail -n 10 /var/log/temperhum-capture.log || true
    echo
    
    # Data file
    echo "Data File Contents:"
    tail -n 5 /tmp/temperhum_data.txt || true
    echo
}

# Main installation function
main() {
    log "Starting TemperhUM sensor integration setup..."
    
    # Check if we're in the right directory
    if [[ ! -d "$PROJECT_ROOT" ]]; then
        error "Project root directory not found: $PROJECT_ROOT"
    fi
    
    # Run setup steps
    check_root
    check_system
    install_dependencies
    setup_udev_rules
    setup_mqtt
    setup_data_files
    setup_service
    test_sensor_detection
    test_data_capture
    start_service
    show_status
    
    log "TemperhUM sensor integration setup completed successfully!"
    echo
    echo "=== Setup Complete ==="
    echo
    echo "Next steps:"
    echo "1. Plug in your TemperhUM sensors"
    echo "2. Configure sensors to different intervals:"
    echo "   - Sensor 1: 1-second intervals"
    echo "   - Sensor 2: 2-second intervals"
    echo "3. Activate sensors manually (hold Caps Lock for 1 second)"
    echo "4. Check Home Assistant for auto-discovered sensors"
    echo
    echo "Useful commands:"
    echo "  - View logs: tail -f /var/log/temperhum-capture.log"
    echo "  - Check service: systemctl status temperhum-capture.service"
    echo "  - Restart service: sudo systemctl restart temperhum-capture.service"
    echo "  - View data: tail -f /tmp/temperhum_data.txt"
    echo
}

# Run main function
main "$@" 