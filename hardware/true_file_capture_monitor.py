#!/usr/bin/env python3
"""
True File Capture TEMPerHUM Monitor
===================================

Monitors TEMPerHUM sensors by truly diverting their output to files
without any terminal display.

Usage:
    python3 true_file_capture_monitor.py
"""

import os
import sys
import time
import json
import subprocess
import re
from datetime import datetime

class TrueFileCaptureMonitor:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1 (Inner)',
                'capture_file': None,
                'status': 'off',
                'current_reading': None
            },
            'sensor_2': {
                'name': 'Sensor 2 (Outer)',
                'capture_file': None,
                'status': 'off',
                'current_reading': None
            }
        }
        self.running = True
        
    def setup_capture_files(self):
        """Setup capture files and create capture commands."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create capture files
        self.sensors['sensor_1']['capture_file'] = f"/tmp/sensor1_{timestamp}.txt"
        self.sensors['sensor_2']['capture_file'] = f"/tmp/sensor2_{timestamp}.txt"
        
        print("🐢 True File Capture TEMPerHUM Monitor")
        print("=" * 50)
        print()
        print("📁 Capture files created:")
        print(f"  Sensor 1: {self.sensors['sensor_1']['capture_file']}")
        print(f"  Sensor 2: {self.sensors['sensor_2']['capture_file']}")
        print()
        print("🚀 Run these commands in separate terminals:")
        print("  (These will capture sensor output to files without showing it)")
        print()
        print(f"  Terminal 1: cat > {self.sensors['sensor_1']['capture_file']}")
        print(f"  Terminal 2: cat > {self.sensors['sensor_2']['capture_file']}")
        print()
        print("  OR use tee to see output AND save to file:")
        print()
        print(f"  Terminal 1: tee {self.sensors['sensor_1']['capture_file']}")
        print(f"  Terminal 2: tee {self.sensors['sensor_2']['capture_file']}")
        print()
        print("  Then activate sensors (TXT button or Num Lock)")
        print("  Press Ctrl+C in capture terminals to stop")
        print()
        print("Press Enter to start monitoring...")
        input()
    
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
                if line:
                    # Parse the data
                    parsed = self.parse_temperhum_data(line)
                    if parsed:
                        return {
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'temperature': parsed['temperature'],
                            'humidity': parsed['humidity'],
                            'raw_data': line
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
        print("🐢 TEMPerHUM Sensor Monitor (File Capture)")
        print("=" * 50)
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
        # Setup capture files
        self.setup_capture_files()
        
        # Main monitoring loop
        try:
            while self.running:
                self.display_status()
                time.sleep(1)  # Update every second
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitor stopped")

def main():
    monitor = TrueFileCaptureMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 