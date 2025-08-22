#!/bin/bash
# TemperhUM Sensor Deployment Script
# Automated deployment for turtle monitoring system

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/shrimp/turtle-monitor"
SERVICE_NAME="temperhum-mqtt"
SERVICE_USER="temperhum"
PYTHON_ENV_PATH="$PROJECT_ROOT/hardware/temperhum_env"

# Logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

check_system() {
    log "Checking system requirements..."
    
    # Check Ubuntu version
    if ! grep -q "Ubuntu" /etc/os-release; then
        warning "This script is designed for Ubuntu, proceeding anyway..."
    fi
    
    # Check if sensors are connected
    if ! lsusb | grep -q "3553:a001"; then
        error "TemperhUM sensors not detected. Please connect USB sensors and try again."
    fi
    
    success "System requirements met"
}

install_dependencies() {
    log "Installing system dependencies..."
    
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        udev \
        systemd
    
    success "Dependencies installed"
}

create_service_user() {
    log "Creating service user..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d /nonexistent -c "TemperhUM Service User" "$SERVICE_USER"
        success "Created service user: $SERVICE_USER"
    else
        log "Service user already exists"
    fi
}

setup_udev_rules() {
    log "Setting up USB device permissions..."
    
    cat > /etc/udev/rules.d/99-temperhum.rules << 'EOF'
# TemperhUM USB sensors
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="3553", ATTRS{idProduct}=="a001", MODE="0666", GROUP="temperhum"
EOF
    
    # Reload udev rules
    udevadm control --reload-rules
    udevadm trigger
    
    success "USB permissions configured"
}

setup_python_environment() {
    log "Setting up Python environment..."
    
    # Create project directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/hardware"
    
    # Copy service files
    cp -r "$(dirname "$0")/../hardware"/* "$PROJECT_ROOT/hardware/"
    
    # Create Python virtual environment
    if [[ ! -d "$PYTHON_ENV_PATH" ]]; then
        python3 -m venv "$PYTHON_ENV_PATH"
    fi
    
    # Install Python dependencies
    source "$PYTHON_ENV_PATH/bin/activate"
    pip install --upgrade pip
    pip install paho-mqtt
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_ROOT"
    
    success "Python environment configured"
}

create_systemd_service() {
    log "Creating systemd service..."
    
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=TemperhUM MQTT Service for Home Assistant
After=network.target mqtt.service
Wants=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$PROJECT_ROOT/hardware
Environment=PATH=$PYTHON_ENV_PATH/bin
ExecStart=$PYTHON_ENV_PATH/bin/python3 temperhum_mqtt_service.py -c temperhum_config.json
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_ROOT
SupplementaryGroups=dialout

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    success "Systemd service created"
}

setup_logging() {
    log "Setting up logging..."
    
    # Create log directory
    mkdir -p /var/log/temperhum
    chown "$SERVICE_USER:$SERVICE_USER" /var/log/temperhum
    
    # Create logrotate configuration
    cat > /etc/logrotate.d/temperhum << 'EOF'
/var/log/temperhum-mqtt.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    copytruncate
    create 644 temperhum temperhum
}
EOF
    
    success "Logging configured"
}

update_docker_compose() {
    log "Updating Docker Compose configuration..."
    
    DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker/docker-compose.yml"
    
    if [[ -f "$DOCKER_COMPOSE_FILE" ]]; then
        # Backup original
        cp "$DOCKER_COMPOSE_FILE" "$DOCKER_COMPOSE_FILE.backup"
        
        # Add USB device mappings for TemperhUM sensors
        if ! grep -q "hidraw" "$DOCKER_COMPOSE_FILE"; then
            # Find the devices section and add hidraw devices
            sed -i '/devices:/a\      # TemperhUM USB sensors\n      - /dev/hidraw0:/dev/hidraw0\n      - /dev/hidraw1:/dev/hidraw1\n      - /dev/hidraw2:/dev/hidraw2\n      - /dev/hidraw3:/dev/hidraw3' "$DOCKER_COMPOSE_FILE"
        fi
        
        success "Docker Compose updated"
    else
        warning "Docker Compose file not found, skipping update"
    fi
}

test_service() {
    log "Testing service functionality..."
    
    # Test sensor connectivity
    cd "$PROJECT_ROOT/hardware"
    source "$PYTHON_ENV_PATH/bin/activate"
    
    if sudo -u "$SERVICE_USER" python3 temperhum_mqtt_service.py --test; then
        success "Service test passed"
    else
        error "Service test failed"
    fi
}

start_service() {
    log "Starting and enabling service..."
    
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
    
    # Wait a moment and check status
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        success "Service started successfully"
    else
        error "Service failed to start. Check logs: journalctl -u $SERVICE_NAME"
    fi
}

show_status() {
    log "Service status:"
    systemctl status "$SERVICE_NAME" --no-pager
    
    log "Recent logs:"
    journalctl -u "$SERVICE_NAME" -n 10 --no-pager
    
    log "MQTT topics that should appear in Home Assistant:"
    echo "  - homeassistant/sensor/turtle_sensors_sensor1_temp/config"
    echo "  - homeassistant/sensor/turtle_sensors_sensor1_hum/config" 
    echo "  - homeassistant/sensor/turtle_sensors_sensor2_temp/config"
    echo "  - homeassistant/sensor/turtle_sensors_sensor2_hum/config"
    echo "  - turtle/sensors/sensor1/temperature"
    echo "  - turtle/sensors/sensor1/humidity"
    echo "  - turtle/sensors/sensor2/temperature"
    echo "  - turtle/sensors/sensor2/humidity"
}

main() {
    echo "🐢 TemperhUM Sensor Deployment for Turtle Monitoring"
    echo "=================================================="
    
    check_root
    check_system
    install_dependencies
    create_service_user
    setup_udev_rules
    setup_python_environment
    create_systemd_service
    setup_logging
    update_docker_compose
    test_service
    start_service
    
    echo
    success "🎉 TemperhUM sensor service deployed successfully!"
    echo
    log "Next steps:"
    echo "1. Restart Home Assistant to detect new MQTT sensors"
    echo "2. Check Home Assistant UI for new turtle sensor entities"
    echo "3. Monitor service logs: journalctl -u $SERVICE_NAME -f"
    echo
    
    show_status
}

# Handle script arguments
case "${1:-}" in
    "test")
        test_service
        ;;
    "status")
        show_status
        ;;
    "restart")
        systemctl restart "$SERVICE_NAME"
        show_status
        ;;
    "logs")
        journalctl -u "$SERVICE_NAME" -f
        ;;
    *)
        main "$@"
        ;;
esac