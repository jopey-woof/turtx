#!/usr/bin/env python3
"""
🐢 Simple TEMPerHUM Capture
============================
Simple approach - just capture the typed output directly.
Run with: python3 simple_capture.py
"""

import sys
import re
import json
import time
from datetime import datetime

class SimpleCapture:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1',
                'status': 'off',
                'current_reading': None,
                'readings_count': 0,
                'last_activity': None
            },
            'sensor_2': {
                'name': 'Sensor 2', 
                'status': 'off',
                'current_reading': None,
                'readings_count': 0,
                'last_activity': None
            }
        }
        self.total_readings = 0
        self.running = True
        
    def parse_temperhum_data(self, raw_data):
        """Parse TEMPerHUM data format: 29.16 [c]36.08 [%rh]1s"""
        # Updated pattern to handle extra spaces
        pattern = r'(\d+\.?\d*)\s*\[c\]\s*(\d+\.?\d*)\s*\[%rh\]\s*(\d+)s'
        match = re.search(pattern, raw_data, re.IGNORECASE)
        if match:
            try:
                temperature = float(match.group(1))
                humidity = float(match.group(2))
                interval = int(match.group(3))
                return {
                    'temperature': temperature,
                    'humidity': humidity,
                    'interval': interval,
                    'raw_data': raw_data,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            except (ValueError, IndexError):
                pass
        return None
    
    def identify_sensor_from_banner(self, banner_text):
        """Identify sensor type from banner text"""
        if 'inner-temp' in banner_text.lower() or 'inner-hum' in banner_text.lower():
            return 'sensor_1'
        elif 'outer-temp' in banner_text.lower() or 'outer-hum' in banner_text.lower():
            return 'sensor_2'
        else:
            return None
    
    def capture_data(self):
        """Capture data from stdin"""
        print("🐢 Simple TEMPerHUM Capture")
        print("=" * 40)
        print("💡 Press TXT button on sensors to activate them")
        print("Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                try:
                    # Read a line from stdin
                    line = input().strip()
                    if not line:
                        continue
                        
                    print(f"📝 Raw input: '{line}'")
                    
                    # Try to parse as TEMPerHUM data
                    parsed = self.parse_temperhum_data(line)
                    if parsed:
                        # Determine which sensor this is based on timing/context
                        # For now, update both sensors with the same data
                        for sensor_id in self.sensors:
                            self.sensors[sensor_id]['current_reading'] = parsed
                            self.sensors[sensor_id]['readings_count'] += 1
                            self.sensors[sensor_id]['status'] = 'on'
                            self.sensors[sensor_id]['last_activity'] = datetime.now()
                        
                        self.total_readings += 1
                        print(f"📊 Parsed: {parsed['temperature']}°C, {parsed['humidity']}%")
                        self.display_status()
                    else:
                        # Check if this is banner text for identification
                        sensor_id = self.identify_sensor_from_banner(line)
                        if sensor_id:
                            self.sensors[sensor_id]['status'] = 'on'
                            print(f"🏷️ {self.sensors[sensor_id]['name']} identified")
                        
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            self.running = False
            print("\n🛑 Stopping capture...")
            self.display_final_summary()
    
    def display_status(self):
        """Display current sensor status"""
        print("\n" + "="*50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        status_data = {}
        for sensor_id, sensor in self.sensors.items():
            status_data[sensor_id] = {
                'name': sensor['name'],
                'status': sensor['status'],
                'readings_count': sensor['readings_count'],
                'current_reading': sensor['current_reading']
            }
        
        print(json.dumps(status_data, indent=2))
        print("="*50)
    
    def display_final_summary(self):
        """Display final summary when stopping"""
        print("\n📊 FINAL SUMMARY:")
        print("=" * 40)
        for sensor_id, sensor in self.sensors.items():
            print(f"{sensor['name']}:")
            print(f"  Status: {sensor['status']}")
            print(f"  Readings: {sensor['readings_count']}")
            if sensor['current_reading']:
                reading = sensor['current_reading']
                print(f"  Last: {reading['temperature']}°C, {reading['humidity']}%")
            print()
        print(f"Total Readings: {self.total_readings}")

def main():
    print("🐢 Simple TEMPerHUM Capture")
    print("=" * 40)
    print("This script captures typed output from TEMPerHUM sensors.")
    print("Make sure sensors are typing to this terminal.")
    print()
    
    capture = SimpleCapture()
    capture.capture_data()

if __name__ == "__main__":
    main() 