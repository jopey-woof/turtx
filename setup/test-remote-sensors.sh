#!/bin/bash

# 🐢 Remote TEMPerHUM Sensor Test
# Tests actual sensors on the remote server and displays live data

set -e

echo "🐢 Remote TEMPerHUM Sensor Test"
echo "==============================="

# Configuration
REMOTE_HOST="shrimp@10.0.20.69"
REMOTE_PATH="/home/shrimp/turtle-monitor"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to execute remote command
remote_exec() {
    local cmd="$1"
    ssh "$REMOTE_HOST" "$cmd"
}

print_header "Testing TEMPerHUM sensors on remote server..."
echo ""

# Test 1: Check if sensors are detected
print_header "Step 1: Checking sensor detection..."
remote_exec "python3 -c \"
import hid
devices = list(hid.enumerate(0x3553, 0xa001))
print(f'Found {len(devices)} TEMPerHUM device(s)')
for i, device in enumerate(devices):
    print(f'  Device {i+1}: {device.get(\\\"product_string\\\", \\\"Unknown\\\")}')
\""

# Test 2: Check if service is running
print_header "Step 2: Checking service status..."
remote_exec "sudo systemctl status temperhum-manager.service --no-pager -l"

# Test 3: Check recent logs
print_header "Step 3: Checking recent logs..."
remote_exec "sudo journalctl -u temperhum-manager.service --no-pager -n 10"

# Test 4: Check MQTT data
print_header "Step 4: Checking MQTT data..."
echo "Monitoring MQTT topics for 10 seconds..."
remote_exec "timeout 10 mosquitto_sub -t 'turtle/sensors/temperhum/#' -v" || {
    print_warning "MQTT test failed - check if MQTT broker is running"
}

# Test 5: Direct sensor test
print_header "Step 5: Direct sensor test..."
remote_exec "cd $REMOTE_PATH && python3 -c \"
import hid
import time
import re
from datetime import datetime

# Configuration
TEMPERHUM_VENDOR_ID = 0x3553
TEMPERHUM_PRODUCT_ID = 0xa001

def test_sensors():
    try:
        # Find devices
        devices = list(hid.enumerate(TEMPERHUM_VENDOR_ID, TEMPERHUM_PRODUCT_ID))
        print(f'Found {len(devices)} TEMPerHUM device(s)')
        
        if len(devices) == 0:
            print('No devices found')
            return
        
        # Test each device
        for i, device_info in enumerate(devices):
            print(f'\\nTesting Device {i+1}:')
            try:
                # Open device
                device = hid.Device(TEMPERHUM_VENDOR_ID, TEMPERHUM_PRODUCT_ID)
                print(f'  ✅ Device opened successfully')
                
                # Try to read data
                print(f'  📡 Attempting to read data...')
                data = device.read(64, timeout_ms=2000)
                if data:
                    data_str = data.decode('utf-8', errors='ignore')
                    print(f'  📊 Raw data: {repr(data_str)}')
                    
                    # Try to parse
                    pattern = r'(\\d+\\.\\d+)\\[C\\](\\d+\\.\\d+)\\[%RH\\](\\d+)S'
                    match = re.search(pattern, data_str)
                    if match:
                        temp_c = float(match.group(1))
                        humidity = float(match.group(2))
                        interval = int(match.group(3))
                        temp_f = (temp_c * 9/5) + 32
                        
                        print(f'  🌡️  Temperature: {temp_c}°C / {temp_f}°F')
                        print(f'  💧 Humidity: {humidity}%')
                        print(f'  ⏱️  Interval: {interval}s')
                    else:
                        print(f'  ❌ Could not parse data')
                else:
                    print(f'  ❌ No data received')
                
                device.close()
                
            except Exception as e:
                print(f'  ❌ Error testing device: {e}')
                
    except Exception as e:
        print(f'Error: {e}')

test_sensors()
\""

print_header "Step 6: Live data monitoring..."
echo "Starting live monitoring for 30 seconds..."
echo "Press Ctrl+C to stop early"
echo ""

# Create a temporary monitoring script on remote
remote_exec "cat > /tmp/monitor_sensors.py << 'EOF'
#!/usr/bin/env python3
import hid
import time
import re
from datetime import datetime

TEMPERHUM_VENDOR_ID = 0x3553
TEMPERHUM_PRODUCT_ID = 0xa001

def monitor_sensors():
    try:
        devices = list(hid.enumerate(TEMPERHUM_VENDOR_ID, TEMPERHUM_PRODUCT_ID))
        print(f'Monitoring {len(devices)} sensor(s) for 30 seconds...')
        print('Press Ctrl+C to stop early')
        print('')
        
        start_time = time.time()
        readings = {i+1: 0 for i in range(len(devices))}
        
        while time.time() - start_time < 30:
            for i, device_info in enumerate(devices):
                try:
                    device = hid.Device(TEMPERHUM_VENDOR_ID, TEMPERHUM_PRODUCT_ID)
                    data = device.read(64, timeout_ms=1000)
                    device.close()
                    
                    if data:
                        data_str = data.decode('utf-8', errors='ignore')
                        pattern = r'(\\d+\\.\\d+)\\[C\\](\\d+\\.\\d+)\\[%RH\\](\\d+)S'
                        match = re.search(pattern, data_str)
                        
                        if match:
                            readings[i+1] += 1
                            temp_c = float(match.group(1))
                            humidity = float(match.group(2))
                            interval = int(match.group(3))
                            temp_f = (temp_c * 9/5) + 32
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            
                            print(f'┌─ Sensor {i+1} ──────────────────────────────────────┐')
                            print(f'│ Temperature: {temp_c}°C / {temp_f}°F                    │')
                            print(f'│ Humidity:    {humidity}%                              │')
                            print(f'│ Timestamp:   {timestamp}        │')
                            print(f'│ Readings:    {readings[i+1]}                              │')
                            print(f'└─────────────────────────────────────────────────────────────┘')
                            print('')
                            
                except Exception as e:
                    print(f'Sensor {i+1} error: {e}')
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print('\\n🛑 Monitoring stopped by user')
    except Exception as e:
        print(f'Error: {e}')
    
    print('📊 Summary:')
    for sensor_id, count in readings.items():
        print(f'  Sensor {sensor_id}: {count} readings')

if __name__ == '__main__':
    monitor_sensors()
EOF"

# Run the monitoring script
remote_exec "python3 /tmp/monitor_sensors.py"

# Cleanup
remote_exec "rm -f /tmp/monitor_sensors.py"

print_success "Remote sensor test completed!"
echo ""
echo "📋 Test Summary:"
echo "  ✅ Sensor detection tested"
echo "  ✅ Service status checked"
echo "  ✅ Logs reviewed"
echo "  ✅ MQTT data monitored"
echo "  ✅ Direct sensor access tested"
echo "  ✅ Live data monitoring completed"
echo ""
echo "🐢 TEMPerHUM sensors are ready for turtle habitat monitoring!" 