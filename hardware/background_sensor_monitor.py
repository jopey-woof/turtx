#!/usr/bin/env python3
"""
Background TEMPerHUM Sensor Monitor
===================================

Automatically captures TEMPerHUM sensor output to files in the background
and monitors them for status changes and current readings.

Usage:
    python3 background_sensor_monitor.py
"""

import os
import sys
import time
import json
import subprocess
import re
import threading
from datetime import datetime

class BackgroundSensorMonitor:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1 (Inner)',
                'capture_file': None,
                'status': 'off',
                'current_reading': None,
                'capture_process': None
            },
            'sensor_2': {
                'name': 'Sensor 2 (Outer)',
                'capture_file': None,
                'status': 'off',
                'current_reading': None,
                'capture_process': None
            }
        }
        self.running = True
        
    def setup_capture_files(self):
        """Setup capture files for each sensor."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create capture files
        self.sensors['sensor_1']['capture_file'] = f"/tmp/sensor1_{timestamp}.txt"
        self.sensors['sensor_2']['capture_file'] = f"/tmp/sensor2_{timestamp}.txt"
        
        print("🐢 Background TEMPerHUM Sensor Monitor")
        print("=" * 50)
        print()
        print("📁 Capture files created:")
        print(f"  Sensor 1: {self.sensors['sensor_1']['capture_file']}")
        print(f"  Sensor 2: {self.sensors['sensor_2']['capture_file']}")
        print()
        print("🚀 Starting background capture processes...")
        print("   (No additional terminals needed)")
        print()
    
    def start_background_capture(self, sensor_id, capture_file):
        """Start a background process to capture sensor output to file."""
        # Create a simple capture script that runs in background
        script_content = f'''#!/usr/bin/env python3
import sys
import os
from datetime import datetime

output_file = "{capture_file}"

# Create output file
with open(output_file, 'w') as f:
    f.write(f"Background capture started at {{datetime.now()}}\\n")
    f.write(f"Sensor: {sensor_id}\\n")
    f.write("=" * 50 + "\\n")

# Monitor stdin and write to file
try:
    while True:
        try:
            line = input()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%3N')
            with open(output_file, 'a') as f:
                f.write(f"{{timestamp}}: {{line}}\\n")
        except EOFError:
            break
except KeyboardInterrupt:
    pass
'''
        
        script_path = f"/tmp/background_capture_{sensor_id}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        # Start background process
        try:
            # Use nohup to run in background
            cmd = f"nohup python3 {script_path} > /dev/null 2>&1 &"
            subprocess.run(cmd, shell=True)
            
            # Store process info
            self.sensors[sensor_id]['capture_process'] = {
                'script_path': script_path,
                'started_at': datetime.now()
            }
            
            print(f"✅ Started background capture for {sensor_id}")
            
        except Exception as e:
            print(f"❌ Failed to start capture for {sensor_id}: {e}")
    
    def parse_temperhum_data(self, raw_data):
        """Parse TEMPerHUM data."""
        pattern = r'(\d+\.?\d*)\s*\[C\]\s*(\d+\.?\d*)\s*\[%RH\]\s*(\d+)S'
        match = re.search(pattern, raw_data, re.IGNORECASE)
        if match:
            try:
                temperature = float(match.group(1))
                humidity = float(match.group(2))
                return {'temperature': temperature, 'humidity': humidity}
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
                line = line.strip()
                if line and ': ' in line:
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
            
            # Check if file has been modified in the last 5 seconds
            if time.time() - current_mtime < 5:
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
        print("🐢 Background TEMPerHUM Sensor Monitor")
        print("=" * 50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        print()
        print("💡 Activate sensors: Press TXT button or hold Num Lock for 3 seconds")
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
    
    def cleanup_background_processes(self):
        """Clean up background capture processes."""
        print("\n🧹 Cleaning up background processes...")
        
        for sensor_id, sensor in self.sensors.items():
            if sensor['capture_process']:
                script_path = sensor['capture_process']['script_path']
                try:
                    # Kill any processes using this script
                    subprocess.run(f"pkill -f {script_path}", shell=True)
                    # Remove script file
                    if os.path.exists(script_path):
                        os.remove(script_path)
                    print(f"✅ Cleaned up {sensor_id}")
                except:
                    pass
    
    def run(self):
        """Run the background sensor monitor."""
        # Setup capture files
        self.setup_capture_files()
        
        # Start background capture processes
        for sensor_id in self.sensors:
            self.start_background_capture(sensor_id, self.sensors[sensor_id]['capture_file'])
        
        print("✅ Background capture started for both sensors")
        print("   (Sensors will automatically capture to files when activated)")
        print()
        print("Press Enter to start monitoring...")
        input()
        
        # Main monitoring loop
        try:
            while self.running:
                self.display_status()
                time.sleep(1)  # Update every second
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitor stopped")
        finally:
            self.cleanup_background_processes()

def main():
    monitor = BackgroundSensorMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 