#!/bin/bash

# 🐢 Live TEMPerHUM Sensor Test
# Displays real-time data from both TEMPerHUM sensors

set -e

echo "🐢 Live TEMPerHUM Sensor Test"
echo "============================"

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

print_sensor_data() {
    local sensor_id=$1
    local temp_c=$2
    local temp_f=$3
    local humidity=$4
    local timestamp=$5
    
    echo -e "${CYAN}┌─ Sensor ${sensor_id} ──────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│${NC} Temperature: ${GREEN}${temp_c}°C${NC} / ${GREEN}${temp_f}°F${NC}                    ${CYAN}│${NC}"
    echo -e "${CYAN}│${NC} Humidity:    ${GREEN}${humidity}%${NC}                              ${CYAN}│${NC}"
    echo -e "${CYAN}│${NC} Timestamp:   ${YELLOW}${timestamp}${NC}        ${CYAN}│${NC}"
    echo -e "${CYAN}└─────────────────────────────────────────────────────────────┘${NC}"
}

# Check if Python script exists
if [[ ! -f hardware/temperhum_manager.py ]]; then
    print_error "TEMPerHUM manager script not found"
    exit 1
fi

print_header "Testing live sensor data from TEMPerHUM sensors..."
echo ""

# Create a temporary Python script for live testing
cat > /tmp/test_live_sensors.py << 'EOF'
#!/usr/bin/env python3
"""
Live TEMPerHUM Sensor Test
Displays real-time data from both sensors in a formatted way
"""

import os
import sys
import time
import json
import hid
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Configuration
TEMPERHUM_VENDOR_ID = 0x3553
TEMPERHUM_PRODUCT_ID = 0xa001

class LiveSensorTest:
    def __init__(self):
        self.sensors = []
        self.running = True
        
    def discover_sensors(self) -> int:
        """Discover and initialize TEMPerHUM sensors"""
        try:
            print("🔍 Discovering TEMPerHUM sensors...")
            
            # Find all TEMPerHUM devices
            devices = list(hid.enumerate(TEMPERHUM_VENDOR_ID, TEMPERHUM_PRODUCT_ID))
            
            if not devices:
                print("❌ No TEMPerHUM devices found")
                return 0
            
            print(f"✅ Found {len(devices)} TEMPerHUM device(s)")
            
            # Initialize each sensor
            for i, device_info in enumerate(devices):
                sensor = {
                    'id': i + 1,
                    'path': device_info['path'],
                    'device': None,
                    'is_active': False
                }
                
                if self._initialize_sensor(sensor):
                    self.sensors.append(sensor)
                    print(f"✅ Sensor {i+1} initialized successfully")
                else:
                    print(f"❌ Failed to initialize sensor {i+1}")
            
            print(f"✅ Successfully initialized {len(self.sensors)} sensor(s)")
            return len(self.sensors)
            
        except Exception as e:
            print(f"❌ Error discovering sensors: {e}")
            return 0
    
    def _initialize_sensor(self, sensor: Dict) -> bool:
        """Initialize and activate a sensor"""
        try:
            # Open HID device
            sensor['device'] = hid.Device(TEMPERHUM_VENDOR_ID, TEMPERHUM_PRODUCT_ID)
            
            # Activate sensor (send Caps Lock to toggle ON)
            self._activate_sensor(sensor)
            
            # Wait for banner and validate
            if self._wait_for_banner(sensor):
                sensor['is_active'] = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Failed to initialize sensor {sensor['id']}: {e}")
            return False
    
    def _activate_sensor(self, sensor: Dict):
        """Activate sensor by sending Caps Lock key"""
        try:
            # Send Caps Lock key to toggle sensor ON
            caps_lock_code = 0x39  # Caps Lock key code
            
            # Create HID report for Caps Lock
            report = [0x00, caps_lock_code, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            sensor['device'].write(bytes(report))
            
            # Wait a moment for the key to be processed
            time.sleep(0.1)
            
            # Send key release
            release_report = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            sensor['device'].write(bytes(release_report))
            
        except Exception as e:
            print(f"❌ Failed to activate sensor {sensor['id']}: {e}")
            raise
    
    def _wait_for_banner(self, sensor: Dict, timeout: int = 10) -> bool:
        """Wait for and validate banner output"""
        start_time = time.time()
        banner_detected = False
        
        while time.time() - start_time < timeout:
            try:
                # Read data from device
                data = sensor['device'].read(64, timeout_ms=1000)
                if data:
                    data_str = data.decode('utf-8', errors='ignore')
                    
                    # Check for banner content
                    if "WWW.PCSENSOR.COM" in data_str or "TEMPERHUM" in data_str:
                        banner_detected = True
                        break
                        
            except Exception as e:
                continue
        
        return banner_detected
    
    def read_sensor_data(self, sensor: Dict) -> Optional[Dict]:
        """Read and parse sensor data"""
        if not sensor['is_active'] or not sensor['device']:
            return None
            
        try:
            # Read data from device
            data = sensor['device'].read(64, timeout_ms=1000)
            if not data:
                return None
                
            data_str = data.decode('utf-8', errors='ignore')
            
            # Parse the data
            parsed = self._parse_data(data_str)
            if parsed:
                parsed['sensor_id'] = sensor['id']
                return parsed
                
        except Exception as e:
            print(f"❌ Error reading from sensor {sensor['id']}: {e}")
            
        return None
    
    def _parse_data(self, data_str: str) -> Optional[Dict]:
        """Parse sensor data with robust error handling"""
        try:
            # Remove any banner text that might appear
            data_str = self._clean_data(data_str)
            
            # Look for temperature and humidity pattern
            # Format: XX.XX[C]XX.XX[%RH]XS
            pattern = r'(\d+\.\d+)\[C\](\d+\.\d+)\[%RH\](\d+)S'
            match = re.search(pattern, data_str)
            
            if match:
                temp_c = float(match.group(1))
                humidity = float(match.group(2))
                interval = int(match.group(3))
                
                # Validate data ranges
                if (-40.0 <= temp_c <= 80.0 and 0.0 <= humidity <= 100.0):
                    
                    # Convert to Fahrenheit
                    temp_f = (temp_c * 9/5) + 32
                    
                    return {
                        "temperature_c": round(temp_c, 2),
                        "temperature_f": round(temp_f, 2),
                        "humidity": round(humidity, 2),
                        "interval": interval,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
            else:
                print(f"🔍 No valid data pattern found in: {data_str}")
                
        except Exception as e:
            print(f"❌ Error parsing data: {e}")
            
        return None
    
    def _clean_data(self, data_str: str) -> str:
        """Clean data string by removing banner text and other artifacts"""
        # Remove common banner text
        banner_patterns = [
            r'WWW\.PCSENSOR\.COM.*?INTERVAL',
            r'TEMPERHUM.*?INTERVAL',
            r'CAPS LOCK.*?INTERVAL',
            r'TYPE:.*?INTERVAL'
        ]
        
        for pattern in banner_patterns:
            data_str = re.sub(pattern, '', data_str, flags=re.DOTALL)
        
        # Remove extra whitespace and newlines
        data_str = re.sub(r'\s+', '', data_str)
        
        return data_str
    
    def run_live_test(self, duration: int = 60):
        """Run live sensor test for specified duration"""
        print(f"🚀 Starting live sensor test for {duration} seconds...")
        print("Press Ctrl+C to stop early")
        print("")
        
        start_time = time.time()
        readings = {sensor['id']: 0 for sensor in self.sensors}
        
        try:
            while time.time() - start_time < duration and self.running:
                # Read data from all sensors
                for sensor in self.sensors:
                    if sensor['is_active']:
                        data = self.read_sensor_data(sensor)
                        if data:
                            readings[sensor['id']] += 1
                            
                            # Format timestamp for display
                            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                            display_time = timestamp.strftime('%H:%M:%S')
                            
                            # Print formatted data
                            print(f"┌─ Sensor {data['sensor_id']} ──────────────────────────────────────┐")
                            print(f"│ Temperature: {data['temperature_c']}°C / {data['temperature_f']}°F                    │")
                            print(f"│ Humidity:    {data['humidity']}%                              │")
                            print(f"│ Timestamp:   {display_time}        │")
                            print(f"│ Readings:    {readings[data['sensor_id']]}                              │")
                            print(f"└─────────────────────────────────────────────────────────────┘")
                            print("")
                
                # Wait before next reading
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Live test stopped by user")
        
        # Print summary
        print("📊 Test Summary:")
        for sensor_id, count in readings.items():
            print(f"  Sensor {sensor_id}: {count} readings")
    
    def cleanup(self):
        """Cleanup sensor devices"""
        for sensor in self.sensors:
            if sensor['device']:
                try:
                    sensor['device'].close()
                except:
                    pass

def main():
    """Main entry point"""
    test = LiveSensorTest()
    
    try:
        # Discover sensors
        sensor_count = test.discover_sensors()
        if sensor_count == 0:
            print("❌ No sensors available for testing")
            return
        
        # Run live test
        test.run_live_test(60)  # 60 seconds
        
    except Exception as e:
        print(f"❌ Error during live test: {e}")
    finally:
        test.cleanup()

if __name__ == "__main__":
    main()
EOF

# Make the temporary script executable
chmod +x /tmp/test_live_sensors.py

print_header "Running live sensor test..."
echo "This will display real-time data from both sensors for 60 seconds"
echo "Press Ctrl+C to stop early"
echo ""

# Run the live test
python3 /tmp/test_live_sensors.py

# Cleanup
rm -f /tmp/test_live_sensors.py

print_success "Live sensor test completed!" 