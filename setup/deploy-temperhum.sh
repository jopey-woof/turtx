#!/bin/bash

# 🐢 TEMPerHUM Sensor Deployment Script
# This script deploys the TEMPerHUM sensor system to the remote machine

set -e

echo "🐢 TEMPerHUM Sensor Deployment"
echo "=============================="

# Configuration
REMOTE_HOST="shrimp@10.0.20.69"
REMOTE_DIR="/home/shrimp/turtle-monitor"
REMOTE_PYTHON="/usr/bin/python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting TEMPerHUM deployment...${NC}"

# Step 1: Stop existing service
echo -e "${BLUE}🛑 Stopping existing service...${NC}"
ssh $REMOTE_HOST 'echo shrimp | sudo -S systemctl stop temperhum-manager.service 2>/dev/null || true'

# Step 2: Deploy files to remote machine
echo -e "${BLUE}📁 Deploying files to remote machine...${NC}"

# Create remote directory structure
ssh $REMOTE_HOST "mkdir -p $REMOTE_DIR/hardware"

# Copy manager script
scp hardware/temperhum_manager.py $REMOTE_HOST:$REMOTE_DIR/hardware/
ssh $REMOTE_HOST "chmod +x $REMOTE_DIR/hardware/temperhum_manager.py"

# Copy service file
scp hardware/temperhum-manager.service $REMOTE_HOST:$REMOTE_DIR/hardware/

# Copy udev rules
scp hardware/99-temperhum.rules $REMOTE_HOST:$REMOTE_DIR/hardware/

# Copy installation script
scp setup/install-temperhum.sh $REMOTE_HOST:$REMOTE_DIR/setup/
ssh $REMOTE_HOST "chmod +x $REMOTE_DIR/setup/install-temperhum.sh"

# Copy test script
scp setup/test-temperhum-manager.sh $REMOTE_HOST:$REMOTE_DIR/setup/
ssh $REMOTE_HOST "chmod +x $REMOTE_DIR/setup/test-temperhum-manager.sh"

echo -e "${GREEN}✅ Files deployed successfully${NC}"

# Step 3: Install dependencies and configure system
echo -e "${BLUE}🔧 Installing and configuring system...${NC}"
ssh $REMOTE_HOST "cd $REMOTE_DIR && ./setup/install-temperhum.sh"

# Step 4: Test the installation
echo -e "${BLUE}🧪 Testing installation...${NC}"
ssh $REMOTE_HOST "cd $REMOTE_DIR && ./setup/test-temperhum-manager.sh"

# Step 5: Start the service
echo -e "${BLUE}🚀 Starting TEMPerHUM service...${NC}"
ssh $REMOTE_HOST 'echo shrimp | sudo -S systemctl start temperhum-manager.service'

# Step 6: Verify service is running
echo -e "${BLUE}🔍 Verifying service status...${NC}"
ssh $REMOTE_HOST 'echo shrimp | sudo -S systemctl status temperhum-manager.service --no-pager'

# Step 7: Show monitoring commands
echo ""
echo -e "${GREEN}🎉 TEMPerHUM deployment completed!${NC}"
echo ""
echo -e "${BLUE}📊 Monitoring Commands:${NC}"
echo "  # Check service status"
echo "  ssh $REMOTE_HOST 'sudo systemctl status temperhum-manager.service'"
echo ""
echo "  # Monitor service logs"
echo "  ssh $REMOTE_HOST 'sudo journalctl -u temperhum-manager.service -f'"
echo ""
echo "  # Monitor MQTT topics"
echo "  ssh $REMOTE_HOST 'mosquitto_sub -t \"turtle/sensors/temperhum/#\" -v'"
echo ""
echo "  # Check sensor data files"
echo "  ssh $REMOTE_HOST 'ls -la /tmp/temperhum_data/'"
echo ""
echo "  # Test sensor detection"
echo "  ssh $REMOTE_HOST 'python3 -c \"import evdev; print([d.name for d in [evdev.InputDevice(p) for p in evdev.list_devices()]])\"'"
echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "1. Connect TEMPerHUM sensors to USB ports on the remote machine"
echo "2. Monitor the service logs for sensor detection and activation"
echo "3. Verify MQTT data is being published"
echo "4. Configure Home Assistant to consume the MQTT sensor data"
echo ""
echo -e "${BLUE}🔧 Troubleshooting:${NC}"
echo "  # Restart service"
echo "  ssh $REMOTE_HOST 'sudo systemctl restart temperhum-manager.service'"
echo ""
echo "  # Check for errors"
echo "  ssh $REMOTE_HOST 'sudo journalctl -u temperhum-manager.service --since \"5 minutes ago\"'"
echo ""
echo "  # Re-run tests"
echo "  ssh $REMOTE_HOST 'cd $REMOTE_DIR && ./setup/test-temperhum-manager.sh'" 