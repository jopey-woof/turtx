#!/usr/bin/env python3
"""
Simple TEMPerHUM Monitor
========================

Simple monitor that captures sensor data and displays status.
Uses direct input capture without background processes.

Usage:
    python3 simple_monitor.py
"""

import os
import sys
import time
import json
import subprocess
import re
from datetime import datetime

class SimpleMonitor:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1 (Inner)',
                'status': 'off',
                'current_reading': None,
                'last_activity': None
            },
            'sensor_2': {
                'name': 'Sensor 2 (Outer)',
                'status': 'off',
                'current_reading': None,
                'last_activity': None
            }
        }
        self.running = True
        self.captured_data = []
        
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
        print("🐢 Simple TEMPerHUM Monitor")
        print("=" * 40)
        print("💡 Activate sensors: Press TXT button or hold Num Lock for 3 seconds")
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
                        
                        # Update both sensors since we can't distinguish them
                        for sensor_id, sensor in self.sensors.items():
                            sensor['status'] = 'on'
                            sensor['current_reading'] = {
                                'timestamp': datetime.now().strftime('%H:%M:%S'),
                                'temperature': parsed['temperature'],
                                'humidity': parsed['humidity'],
                                'raw_data': line
                            }
                            sensor['last_activity'] = datetime.now()
                    else:
                        # Banner text - mark sensors as active
                        for sensor_id, sensor in self.sensors.items():
                            sensor['status'] = 'on'
                            sensor['last_activity'] = datetime.now()
                    
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
        print("🐢 Simple TEMPerHUM Monitor")
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
        """Run the monitor."""
        self.capture_and_monitor()
        
        # Final summary
        print("\n📊 FINAL SUMMARY:")
        print("=" * 30)
        for sensor_id, sensor in self.sensors.items():
            print(f"{sensor['name']}:")
            print(f"  Status: {sensor['status']}")
            if sensor['current_reading']:
                reading = sensor['current_reading']
                print(f"  Last: {reading['temperature']:.1f}°C, {reading['humidity']:.1f}%")
            print()
        
        print(f"Total captured: {len(self.captured_data)} lines")

def main():
    monitor = SimpleMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 