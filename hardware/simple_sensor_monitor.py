#!/usr/bin/env python3
"""
Simple TEMPerHUM Sensor Monitor
===============================

Monitors two TEMPerHUM sensors by diverting their output to files
and displaying current readings in JSON format.

Usage:
    python3 simple_sensor_monitor.py
"""

import os
import sys
import time
import json
import subprocess
import re
from datetime import datetime

class SimpleSensorMonitor:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1 (Inner)',
                'usb_path': None,
                'capture_file': None,
                'last_modified': None,
                'status': 'off',
                'current_reading': None
            },
            'sensor_2': {
                'name': 'Sensor 2 (Outer)',
                'usb_path': None,
                'capture_file': None,
                'last_modified': None,
                'status': 'off',
                'current_reading': None
            }
        }
        self.running = True
        
    def find_temperhum_devices(self):
        """Find TEMPerHUM devices."""
        result = subprocess.run("lsusb | grep -i temperhum", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return []
        
        devices = []
        for line in result.stdout.split('\n'):
            if line.strip():
                devices.append(line.strip())
        return devices
    
    def setup_capture_files(self):
        """Setup capture files for each sensor."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create capture files
        self.sensors['sensor_1']['capture_file'] = f"/tmp/sensor1_{timestamp}.txt"
        self.sensors['sensor_2']['capture_file'] = f"/tmp/sensor2_{timestamp}.txt"
        
        # Create capture scripts
        self.create_capture_script('sensor_1', self.sensors['sensor_1']['capture_file'])
        self.create_capture_script('sensor_2', self.sensors['sensor_2']['capture_file'])
        
        print("📁 Capture files created:")
        print(f"  Sensor 1: {self.sensors['sensor_1']['capture_file']}")
        print(f"  Sensor 2: {self.sensors['sensor_2']['capture_file']}")
        print()
        print("🚀 Run these commands in separate terminals:")
        print(f"  Terminal 1: python3 /tmp/capture_sensor1.py")
        print(f"  Terminal 2: python3 /tmp/capture_sensor2.py")
        print()
    
    def create_capture_script(self, sensor_id, output_file):
        """Create a simple capture script that diverts output to file."""
        script_content = f'''#!/usr/bin/env python3
import sys
from datetime import datetime

output_file = "{output_file}"

print(f"Starting capture for {sensor_id} to {{output_file}}")
print("Press TXT button on sensor or hold Num Lock for 3 seconds")
print("Press Ctrl+C to stop")

try:
    with open(output_file, 'w') as f:
        f.write(f"Capture started at {{datetime.now()}}\\n")
        
        while True:
            try:
                line = input().strip()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%3N')
                f.write(f"{{timestamp}}: {{line}}\\n")
                f.flush()
            except EOFError:
                break
except KeyboardInterrupt:
    print("\\nCapture stopped")
'''
        
        script_path = f"/tmp/capture_{sensor_id}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
    
    def parse_temperhum_data(self, raw_data):
        """Parse TEMPerHUM data."""
        pattern = r'(\\d+\\.?\\d*)\\s*\\[C\\]\\s*(\\d+\\.?\\d*)\\s*\\[%RH\\]\\s*(\\d+)S'
        match = re.search(pattern, raw_data, re.IGNORECASE)
        if match:
            try:
                temperature = float(match.group(1))
                humidity = float(match.group(2))
                return {{'temperature': temperature, 'humidity': humidity}}
            except (ValueError, IndexError):
                pass
        return None
    
    def get_latest_reading(self, capture_file):
        """Get the latest reading from a capture file."""
        if not os.path.exists(capture_file):
            return None
        
        try:
            with open(capture_file, 'r') as f:
                lines = f.readlines()
                
            # Look for the last temperature/humidity reading
            for line in reversed(lines):
                if ': ' in line:
                    timestamp_str, data = line.split(': ', 1)
                    data = data.strip()
                    
                    # Parse the data
                    parsed = self.parse_temperhum_data(data)
                    if parsed:
                        return {
                            'timestamp': timestamp_str.strip(),
                            'temperature': parsed['temperature'],
                            'humidity': parsed['humidity'],
                            'raw_data': data
                        }
        except Exception as e:
            pass
        
        return None
    
    def check_sensor_status(self, capture_file):
        """Check if sensor is active by monitoring file changes."""
        if not os.path.exists(capture_file):
            return 'off'
        
        try:
            current_mtime = os.path.getmtime(capture_file)
            
            # Check if file has been modified in the last 10 seconds
            if time.time() - current_mtime < 10:
                return 'on'
            else:
                return 'off'
        except:
            return 'off'
    
    def update_sensor_data(self):
        """Update sensor data from capture files."""
        for sensor_id, sensor in self.sensors.items():
            if sensor['capture_file']:
                # Check status
                sensor['status'] = self.check_sensor_status(sensor['capture_file'])
                
                # Get latest reading
                reading = self.get_latest_reading(sensor['capture_file'])
                if reading:
                    sensor['current_reading'] = reading
                else:
                    sensor['current_reading'] = None
    
    def display_status(self):
        """Display current sensor status in JSON format."""
        self.update_sensor_data()
        
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Display status
        print("🐢 TEMPerHUM Sensor Monitor")
        print("=" * 40)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Create JSON output
        status_data = {}
        for sensor_id, sensor in self.sensors.items():
            status_data[sensor_id] = {
                'name': sensor['name'],
                'status': sensor['status'],
                'current_reading': sensor['current_reading']
            }
        
        # Display as formatted JSON
        print(json.dumps(status_data, indent=2))
        print()
        print("Press Ctrl+C to stop")
    
    def run(self):
        """Run the sensor monitor."""
        print("🐢 Simple TEMPerHUM Sensor Monitor")
        print("=" * 40)
        
        # Check for sensors
        devices = self.find_temperhum_devices()
        if len(devices) >= 2:
            print(f"✅ Found {len(devices)} TEMPerHUM sensors")
            for device in devices:
                print(f"  {device}")
        else:
            print(f"⚠️ Found {len(devices)} TEMPerHUM sensors")
        
        print()
        
        # Setup capture files
        self.setup_capture_files()
        
        # Main monitoring loop
        try:
            while self.running:
                self.display_status()
                time.sleep(2)  # Update every 2 seconds
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitor stopped")

def main():
    monitor = SimpleSensorMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 