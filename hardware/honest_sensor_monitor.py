#!/usr/bin/env python3
"""
Honest TEMPerHUM Sensor Monitor
===============================

Monitors TEMPerHUM sensors with honest acknowledgment that we can't
distinguish between two sensors that produce identical data format.

Usage:
    python3 honest_sensor_monitor.py
"""

import os
import sys
import time
import json
import subprocess
import re
from datetime import datetime

class HonestSensorMonitor:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1',
                'usb_path': None,
                'status': 'off',
                'current_reading': None,
                'last_activity': None
            },
            'sensor_2': {
                'name': 'Sensor 2', 
                'usb_path': None,
                'status': 'off',
                'current_reading': None,
                'last_activity': None
            }
        }
        self.running = True
        self.captured_data = []
        self.total_readings = 0
        
    def find_temperhum_devices(self):
        """Find TEMPerHUM devices."""
        print("🔍 Finding TEMPerHUM devices...")
        
        result = subprocess.run("lsusb | grep -i temperhum", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            devices = result.stdout.strip().split('\n')
            for i, device in enumerate(devices):
                if device:
                    print(f"✅ Found: {device}")
                    # Assign USB paths if we can extract them
                    if i < 2:
                        sensor_id = f'sensor_{i+1}'
                        self.sensors[sensor_id]['usb_path'] = f"USB Device {i+1}"
            return len(devices)
        else:
            print("❌ No TEMPerHUM devices found")
            return 0
    
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
    
    def capture_and_monitor(self):
        """Capture sensor input and monitor in real-time."""
        print("🐢 Honest TEMPerHUM Sensor Monitor")
        print("=" * 50)
        print("💡 Activate sensors: Press TXT button or hold Num Lock for 3 seconds")
        print("📝 Note: Both sensors produce identical data format")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while self.running:
                try:
                    # Capture input
                    line = input().strip()
                    if not line:
                        continue
                    
                    # Store captured data
                    data_point = {
                        'timestamp': datetime.now().isoformat(),
                        'raw_data': line
                    }
                    self.captured_data.append(data_point)
                    
                    # Parse data
                    parsed = self.parse_temperhum_data(line)
                    if parsed:
                        data_point['parsed'] = parsed
                        self.total_readings += 1
                        
                        # Update both sensors since we can't distinguish them
                        current_reading = {
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'temperature': parsed['temperature'],
                            'humidity': parsed['humidity'],
                            'raw_data': line
                        }
                        
                        for sensor_id, sensor in self.sensors.items():
                            sensor['status'] = 'on'
                            sensor['current_reading'] = current_reading
                            sensor['last_activity'] = datetime.now()
                        
                        print(f"✅ Sensor Reading: {parsed['temperature']:.1f}°C, {parsed['humidity']:.1f}%")
                    else:
                        # Banner text - mark sensors as active
                        for sensor_id, sensor in self.sensors.items():
                            sensor['status'] = 'on'
                            sensor['last_activity'] = datetime.now()
                        print(f"📝 Banner: {line}")
                    
                    # Display current status
                    self.display_status()
                    
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            self.running = False
    
    def display_status(self):
        """Display current sensor status in JSON format."""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Display status
        print("🐢 Honest TEMPerHUM Sensor Monitor")
        print("=" * 50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Total Readings: {self.total_readings}")
        print()
        print("📝 Note: Both sensors produce identical data format")
        print("   We cannot distinguish which sensor is which")
        print()
        
        # Create JSON output
        status_data = {}
        for sensor_id, sensor in self.sensors.items():
            status_data[sensor_id] = {
                'name': sensor['name'],
                'usb_path': sensor['usb_path'],
                'status': sensor['status'],
                'current_reading': sensor['current_reading']
            }
        
        # Display as formatted JSON
        print(json.dumps(status_data, indent=2))
        print()
        print("Press Ctrl+C to stop")
    
    def run(self):
        """Run the monitor."""
        # Find devices
        device_count = self.find_temperhum_devices()
        print(f"\n📊 Found {device_count} TEMPerHUM device(s)")
        print()
        
        # Start capture and monitoring
        self.capture_and_monitor()
        
        # Final summary
        print("\n📊 FINAL SUMMARY:")
        print("=" * 40)
        print(f"Total Readings: {self.total_readings}")
        print(f"Total Captured: {len(self.captured_data)} lines")
        print()
        
        for sensor_id, sensor in self.sensors.items():
            print(f"{sensor['name']}:")
            print(f"  USB Path: {sensor['usb_path']}")
            print(f"  Status: {sensor['status']}")
            if sensor['current_reading']:
                reading = sensor['current_reading']
                print(f"  Last: {reading['temperature']:.1f}°C, {reading['humidity']:.1f}%")
            print()
        
        print("💡 Note: Both sensors show identical readings because")
        print("   they produce the same data format and we cannot")
        print("   distinguish between them programmatically.")

def main():
    monitor = HonestSensorMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 