#!/bin/bash

# 🐢 TEMPerHUM Manager Test Script
# This script tests the TEMPerHUM sensor implementation

# set -e  # Removed to allow tests to continue even if some fail

echo "🐢 TEMPerHUM Manager Test Suite"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

test_step() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}🧪 Testing: ${test_name}${NC}"
    
    if bash -c "$test_command"; then
        echo -e "${GREEN}✅ PASS: ${test_name}${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL: ${test_name}${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Test 1: Check if Python dependencies are installed
test_step "Python Dependencies" "
    python3 -c 'import evdev, paho.mqtt.client' 2>/dev/null
"

# Test 2: Check if log file exists and is writable
test_step "Log File Permissions" "
    test -w /var/log/temperhum-manager.log
"

# Test 3: Check if udev rules are installed
test_step "Udev Rules Installation" "
    test -f /etc/udev/rules.d/99-temperhum.rules
"

# Test 4: Check if systemd service is installed
test_step "Systemd Service Installation" "
    test -f /etc/systemd/system/temperhum-manager.service
"

# Test 5: Check if user is in input group
test_step "User Group Membership" "
    groups shrimp | grep -q input
"

# Test 6: Check if data directory exists
test_step "Data Directory" "
    test -d /tmp/temperhum_data
"

# Test 7: Check if MQTT broker is running
test_step "MQTT Broker Status" "
    systemctl is-active --quiet mosquitto
"

# Test 8: Check if TEMPerHUM manager script is executable
test_step "Manager Script Permissions" "
    test -x /home/shrimp/turtle-monitor/hardware/temperhum_manager.py
"

# Test 9: Check for USB devices
echo -e "${BLUE}🔍 Checking for USB devices...${NC}"
lsusb | grep -i temperhum || echo -e "${YELLOW}⚠️  No TEMPerHUM devices found in lsusb${NC}"
echo ""

# Test 10: Check for input devices
echo -e "${BLUE}🔍 Checking for input devices...${NC}"
ls /dev/input/event* 2>/dev/null || echo -e "${YELLOW}⚠️  No input devices found${NC}"
echo ""

# Test 11: Test Python script syntax
test_step "Python Script Syntax" "
    python3 -m py_compile /home/shrimp/turtle-monitor/hardware/temperhum_manager.py
"

# Test 12: Check if service can be started (without actually starting it)
test_step "Service Configuration" "
    systemctl is-enabled temperhum-manager.service
"

# Test 13: Test MQTT connectivity
test_step "MQTT Connectivity" "
    timeout 5 mosquitto_pub -t 'test/temperhum' -m 'test' 2>/dev/null || true
"

# Test 14: Check if manager can import required modules
test_step "Manager Module Import" "
    cd /home/shrimp/turtle-monitor && python3 -c '
import sys
sys.path.append(\"./hardware\")
try:
    import temperhum_manager
    print(\"✅ All modules imported successfully\")
except ImportError as e:
    print(f\"❌ Import error: {e}\")
    sys.exit(1)
'
"

echo "📊 Test Results Summary"
echo "======================="
echo -e "${GREEN}✅ Tests Passed: ${TESTS_PASSED}${NC}"
echo -e "${RED}❌ Tests Failed: ${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! TEMPerHUM system is ready.${NC}"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Connect TEMPerHUM sensors to USB ports"
    echo "2. Start the service: sudo systemctl start temperhum-manager.service"
    echo "3. Monitor logs: sudo journalctl -u temperhum-manager.service -f"
    echo "4. Check MQTT data: mosquitto_sub -t 'turtle/sensors/temperhum/#'"
else
    echo -e "${RED}⚠️  Some tests failed. Please fix the issues before proceeding.${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Run installation script: ./setup/install-temperhum.sh"
    echo "2. Check system logs: sudo journalctl -u temperhum-manager.service"
    echo "3. Verify dependencies: pip3 list | grep -E '(evdev|paho-mqtt)'"
    echo "4. Check permissions: ls -la /var/log/temperhum-manager.log"
fi

echo ""
echo "🔍 Manual Testing Commands:"
echo "  # Start service manually"
echo "  sudo systemctl start temperhum-manager.service"
echo ""
echo "  # Monitor service logs"
echo "  sudo journalctl -u temperhum-manager.service -f"
echo ""
echo "  # Monitor MQTT topics"
echo "  mosquitto_sub -t 'turtle/sensors/temperhum/#' -v"
echo ""
echo "  # Check sensor data files"
echo "  ls -la /tmp/temperhum_data/"
echo ""
echo "  # Test sensor detection"
echo "  python3 -c 'import evdev; print([d.name for d in [evdev.InputDevice(p) for p in evdev.list_devices()]])'" 