#!/bin/bash
# TEMPerHUM Test Script Deployer
# ==============================
# This script deploys and runs the TEMPerHUM test installer on the remote machine

set -e

# Configuration
REMOTE_HOST="shrimp@10.0.20.69"
REMOTE_DIR="/home/shrimp/turtle-monitor"
SCRIPT_NAME="temperhum_test_installer.py"
LOCAL_SCRIPT="hardware/temperhum_test_installer.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}=========================================="
    echo -e "  $1"
    echo -e "==========================================${NC}\n"
}

print_step() {
    echo -e "${BLUE}→ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if script exists
if [ ! -f "$LOCAL_SCRIPT" ]; then
    print_error "Test script not found: $LOCAL_SCRIPT"
    exit 1
fi

print_header "TEMPerHUM Test Script Deployer"

print_step "Checking SSH connectivity..."
if ! ssh -o ConnectTimeout=5 "$REMOTE_HOST" "echo 'SSH connection successful'" > /dev/null 2>&1; then
    print_error "Cannot connect to $REMOTE_HOST"
    print_info "Please check:"
    print_info "1. SSH keys are set up"
    print_info "2. Remote machine is accessible"
    print_info "3. User 'shrimp' exists on remote machine"
    exit 1
fi
print_success "SSH connection established"

print_step "Creating remote directory structure..."
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_DIR/hardware"

print_step "Copying test script to remote machine..."
scp "$LOCAL_SCRIPT" "$REMOTE_HOST:$REMOTE_DIR/hardware/"
print_success "Script copied successfully"

print_step "Setting executable permissions..."
ssh "$REMOTE_HOST" "chmod +x $REMOTE_DIR/hardware/$SCRIPT_NAME"

print_header "Running TEMPerHUM Test on Remote Machine"

print_info "The test script will now run on the remote machine."
print_info "You will be prompted to:"
print_info "1. Plug in TEMPerHUM sensors"
print_info "2. Follow interactive instructions"
print_info "3. Test each sensor individually"
print_info ""
print_info "Press Ctrl+C at any time to stop the test."

# Run the test script on the remote machine
ssh -t "$REMOTE_HOST" "cd $REMOTE_DIR/hardware && python3 $SCRIPT_NAME"

print_header "Test Complete"

print_info "Test results are saved on the remote machine in:"
print_info "/tmp/temperhum_test_results_*.json"
print_info ""
print_info "To view results:"
print_info "ssh $REMOTE_HOST 'ls -la /tmp/temperhum_test_results_*.json'"
print_info ""
print_info "To view latest results:"
print_info "ssh $REMOTE_HOST 'cat /tmp/temperhum_test_results_*.json | tail -20'"

print_success "Deployment and testing complete!" 