#!/bin/bash
# 🐢 Turtle Monitor Camera Deployment Script
# Deploys the enhanced turtle monitoring system with camera integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_ROOT/config"
UDEV_RULES_FILE="$CONFIG_DIR/udev-camera.rules"
UDEV_TARGET="/etc/udev/rules.d/99-turtle-camera.rules"

echo -e "${BLUE}🎥 Turtle Monitor Camera Deployment${NC}"
echo "=================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root for udev rules
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root - this is required for udev rules installation"
    else
        print_error "This script must be run as root for udev rules installation"
        print_info "Please run: sudo $0"
        exit 1
    fi
}

# Check camera hardware
check_camera_hardware() {
    print_info "Checking camera hardware..."
    
    # Check for video devices
    local video_devices=()
    for i in {0..3}; do
        if [[ -e "/dev/video$i" ]]; then
            video_devices+=("/dev/video$i")
        fi
    done
    
    if [[ ${#video_devices[@]} -eq 0 ]]; then
        print_error "No camera devices detected at /dev/video*"
        print_info "Please ensure the Arducam USB camera is connected"
        return 1
    fi
    
    print_status "Found camera devices: ${video_devices[*]}"
    
    # Try to get camera information
    if command -v v4l2-ctl &> /dev/null; then
        print_info "Getting camera information..."
        for device in "${video_devices[@]}"; do
            echo "--- $device ---"
            v4l2-ctl -d "$device" --list-devices 2>/dev/null || true
        done
    else
        print_warning "v4l2-ctl not available - cannot get detailed camera info"
    fi
    
    return 0
}

# Install udev rules
install_udev_rules() {
    print_info "Installing udev rules for camera..."
    
    if [[ ! -f "$UDEV_RULES_FILE" ]]; then
        print_error "Udev rules file not found: $UDEV_RULES_FILE"
        return 1
    fi
    
    # Copy udev rules
    cp "$UDEV_RULES_FILE" "$UDEV_TARGET"
    chmod 644 "$UDEV_TARGET"
    
    # Reload udev rules
    udevadm control --reload-rules
    udevadm trigger
    
    print_status "Udev rules installed and reloaded"
}

# Create turtle group if it doesn't exist
create_turtle_group() {
    print_info "Setting up turtle group..."
    
    if ! getent group turtle > /dev/null 2>&1; then
        groupadd turtle
        print_status "Created turtle group"
    else
        print_info "Turtle group already exists"
    fi
    
    # Add current user to turtle group
    local current_user=$(who am i | awk '{print $1}')
    if [[ -n "$current_user" ]]; then
        usermod -a -G turtle "$current_user" 2>/dev/null || true
        print_info "Added user $current_user to turtle group"
    fi
}

# Check Docker installation
check_docker() {
    print_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_info "Please install Docker first: https://docs.docker.com/get-docker/"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running or user not in docker group"
        print_info "Please start Docker and add user to docker group"
        return 1
    fi
    
    print_status "Docker is available and running"
}

# Deploy the system
deploy_system() {
    print_info "Deploying turtle monitor system with camera..."
    
    # Change to deployment directory
    cd "$SCRIPT_DIR"
    
    # Stop existing containers
    print_info "Stopping existing containers..."
    docker-compose down 2>/dev/null || true
    
    # Build and start containers
    print_info "Building and starting containers..."
    docker-compose up --build -d
    
    # Wait for services to start
    print_info "Waiting for services to start..."
    sleep 30
    
    # Check service health
    print_info "Checking service health..."
    
    # Check API health
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        print_status "API service is healthy"
    else
        print_warning "API service health check failed"
    fi
    
    # Check Nginx health
    if curl -f http://localhost/health &> /dev/null; then
        print_status "Nginx service is healthy"
    else
        print_warning "Nginx service health check failed"
    fi
    
    # Check camera status
    if curl -f http://localhost:8000/api/camera/status &> /dev/null; then
        print_status "Camera API endpoint is responding"
    else
        print_warning "Camera API endpoint not responding"
    fi
}

# Test camera functionality
test_camera() {
    print_info "Testing camera functionality..."
    
    # Wait a bit for camera to initialize
    sleep 10
    
    # Test camera status
    if curl -f http://localhost:8000/api/camera/status &> /dev/null; then
        print_status "Camera status endpoint working"
        
        # Get camera status
        local status=$(curl -s http://localhost:8000/api/camera/status | jq -r '.camera.connected' 2>/dev/null || echo "false")
        
        if [[ "$status" == "true" ]]; then
            print_status "Camera is connected and working"
        else
            print_warning "Camera is not connected - check hardware connection"
        fi
    else
        print_warning "Camera status endpoint not working"
    fi
    
    # Test camera snapshot
    if curl -f http://localhost:8000/api/camera/snapshot &> /dev/null; then
        print_status "Camera snapshot endpoint working"
    else
        print_warning "Camera snapshot endpoint not working"
    fi
}

# Show deployment summary
show_summary() {
    echo ""
    echo -e "${GREEN}🎉 Turtle Monitor Camera Deployment Complete!${NC}"
    echo "=========================================="
    echo ""
    echo -e "${BLUE}Access Points:${NC}"
    echo "  • Dashboard: http://$(hostname -I | awk '{print $1}'):80"
    echo "  • API: http://$(hostname -I | awk '{print $1}'):8000"
    echo "  • Camera Status: http://$(hostname -I | awk '{print $1}'):8000/api/camera/status"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  • View logs: docker-compose logs -f"
    echo "  • Restart: docker-compose restart"
    echo "  • Stop: docker-compose down"
    echo "  • Camera restart: curl http://localhost:8000/api/camera/restart"
    echo ""
    echo -e "${BLUE}Camera Features:${NC}"
    echo "  • Live video stream: /api/camera/stream"
    echo "  • Snapshot capture: /api/camera/snapshot"
    echo "  • Auto IR night vision detection"
    echo "  • Automatic USB reconnection"
    echo "  • Health monitoring with 60s max recovery"
    echo ""
    echo -e "${YELLOW}Note:${NC} Camera may take a few minutes to fully initialize"
    echo ""
}

# Main deployment process
main() {
    echo "Starting deployment at $(date)"
    echo ""
    
    # Check prerequisites
    check_root
    check_docker
    
    # Hardware and system setup
    check_camera_hardware || {
        print_warning "Camera hardware check failed - continuing with deployment"
        print_info "Camera functionality will be limited until hardware is connected"
    }
    
    create_turtle_group
    install_udev_rules
    
    # Deploy system
    deploy_system
    
    # Test camera
    test_camera
    
    # Show summary
    show_summary
    
    echo -e "${GREEN}Deployment completed at $(date)${NC}"
}

# Run main function
main "$@" 