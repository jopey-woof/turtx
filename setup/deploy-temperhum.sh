#!/bin/bash
# TemperhUM Sensor Remote Deployment Script
# Deploys the complete sensor integration to the remote Ubuntu server

set -e  # Exit on any error

# Configuration
REMOTE_HOST="shrimp@10.0.20.69"
REMOTE_PROJECT="/home/shrimp/turtle-monitor"
LOCAL_PROJECT="$(pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check SSH connectivity
check_ssh() {
    log "Checking SSH connectivity to $REMOTE_HOST..."
    
    if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$REMOTE_HOST" "echo 'SSH connection successful'" 2>/dev/null; then
        error "Cannot connect to $REMOTE_HOST via SSH"
    fi
    
    log "SSH connection verified"
}

# Sync project files
sync_files() {
    log "Syncing project files to remote server..."
    
    # Create remote directories if they don't exist
    ssh "$REMOTE_HOST" "mkdir -p $REMOTE_PROJECT/hardware $REMOTE_PROJECT/setup"
    
    # Sync hardware files
    rsync -avz --progress \
        hardware/temperhum_manager.py \
        hardware/hid_controller.py \
        hardware/simple_data_capture.py \
        hardware/requirements.txt \
        hardware/99-temperhum-sensors.rules \
        hardware/temperhum-capture.service \
        "$REMOTE_HOST:$REMOTE_PROJECT/hardware/"
    
    # Sync setup files
    rsync -avz --progress \
        setup/install-temperhum.sh \
        "$REMOTE_HOST:$REMOTE_PROJECT/setup/"
    
    log "Files synced successfully"
}

# Run remote installation
run_installation() {
    log "Running remote installation..."
    
    ssh "$REMOTE_HOST" "cd $REMOTE_PROJECT && chmod +x setup/install-temperhum.sh && ./setup/install-temperhum.sh"
    
    log "Remote installation completed"
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    
    # Check service status
    ssh "$REMOTE_HOST" "systemctl is-active temperhum-capture.service" || {
        warning "TemperhUM capture service is not running"
    }
    
    # Check MQTT broker
    ssh "$REMOTE_HOST" "systemctl is-active mosquitto" || {
        warning "MQTT broker is not running"
    }
    
    # Check log file
    ssh "$REMOTE_HOST" "tail -n 5 /var/log/temperhum-capture.log" || {
        warning "Log file not found or empty"
    }
    
    log "Installation verification completed"
}

# Show remote status
show_remote_status() {
    log "Showing remote system status..."
    
    ssh "$REMOTE_HOST" "cd $REMOTE_PROJECT && echo '=== Remote System Status ===' && systemctl status temperhum-capture.service --no-pager -l && echo && systemctl status mosquitto --no-pager -l && echo && echo '=== Recent Logs ===' && tail -n 10 /var/log/temperhum-capture.log"
}

# Main deployment function
main() {
    log "Starting TemperhUM sensor remote deployment..."
    
    # Check if we're in the project directory
    if [[ ! -f "setup/install-temperhum.sh" ]]; then
        error "Please run this script from the project root directory"
    fi
    
    # Run deployment steps
    check_ssh
    sync_files
    run_installation
    verify_installation
    show_remote_status
    
    log "TemperhUM sensor remote deployment completed successfully!"
    echo
    echo "=== Deployment Complete ==="
    echo
    echo "Next steps on remote server:"
    echo "1. Plug in your TemperhUM sensors"
    echo "2. Configure sensors to different intervals:"
    echo "   - Sensor 1: 1-second intervals"
    echo "   - Sensor 2: 2-second intervals"
    echo "3. Activate sensors manually (hold Caps Lock for 1 second)"
    echo "4. Check Home Assistant for auto-discovered sensors"
    echo
    echo "Remote commands:"
    echo "  - SSH to server: ssh $REMOTE_HOST"
    echo "  - View logs: tail -f /var/log/temperhum-capture.log"
    echo "  - Check service: systemctl status temperhum-capture.service"
    echo "  - Restart service: sudo systemctl restart temperhum-capture.service"
    echo "  - View data: tail -f /tmp/temperhum_data.txt"
    echo
}

# Run main function
main "$@" 