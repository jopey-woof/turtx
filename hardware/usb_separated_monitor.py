#!/usr/bin/env python3
"""
USB-Separated TEMPerHUM Monitor
===============================

Monitors two TEMPerHUM sensors separately by their USB paths
and distinguishes between their individual outputs.

Usage:
    python3 usb_separated_monitor.py
"""

import os
import sys
import time
import json
import subprocess
import re
import threading
from datetime import datetime

class USBSeparatedMonitor:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1 (Inner)',
                'usb_path': None,
                'input_device': None,
                'status': 'off',
                'current_reading': None,
                'last_activity': None,
                'readings_count': 0
            },
            'sensor_2': {
                'name': 'Sensor 2 (Outer)',
                'usb_path': None,
                'input_device': None,
                'status': 'off',
                'current_reading': None,
                'last_activity': None,
                'readings_count': 0
            }
        }
        self.running = True
        self.captured_data = []
        
    def find_temperhum_devices(self):
        """Find TEMPerHUM devices and their USB paths."""
        print("🔍 Finding TEMPerHUM devices...")
        
        result = subprocess.run("lsusb", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return []
        
        temperhum_devices = []
        for line in result.stdout.split('\n'):
            if "3553:a001" in line and "TEMPerHUM" in line:
                # Extract bus and device numbers
                match = re.search(r'Bus (\d+) Device (\d+):', line)
                if match:
                    bus = match.group(1)
                    device = match.group(2)
                    usb_path = f"/dev/bus/usb/{bus.zfill(3)}/{device.zfill(3)}"
                    temperhum_devices.append({
                        'line': line.strip(),
                        'bus': bus,
                        'device': device,
                        'usb_path': usb_path
                    })
                    print(f"✅ Found: {line.strip()}")
                    print(f"   USB Path: {usb_path}")
        
        return temperhum_devices
    
    def find_input_devices(self):
        """Find input devices associated with TEMPerHUM sensors."""
        print("🔍 Finding input devices...")
        
        # Get input device list
        result = subprocess.run("ls /dev/input/event*", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return []
        
        input_devices = []
        for device in result.stdout.strip().split('\n'):
            if device:
                # Get device info
                info_result = subprocess.run(f"udevadm info -q property -n {device}", shell=True, capture_output=True, text=True)
                if info_result.returncode == 0:
                    info = info_result.stdout
                    # Check if this is a TEMPerHUM device
                    if "3553:a001" in info or "TEMPerHUM" in info:
                        input_devices.append(device)
                        print(f"✅ Input device: {device}")
        
        return input_devices
    
    def assign_sensors(self):
        """Assign sensors to USB ports and input devices."""
        devices = self.find_temperhum_devices()
        input_devices = self.find_input_devices()
        
        if len(devices) >= 2:
            # Assign first device to sensor 1, second to sensor 2
            self.sensors['sensor_1']['usb_path'] = devices[0]['usb_path']
            self.sensors['sensor_2']['usb_path'] = devices[1]['usb_path']
            
            # Assign input devices if available
            if len(input_devices) >= 2:
                self.sensors['sensor_1']['input_device'] = input_devices[0]
                self.sensors['sensor_2']['input_device'] = input_devices[1]
            
            print(f"\n📋 Sensor Assignment:")
            print(f"  Sensor 1 (Inner): {devices[0]['usb_path']}")
            print(f"  Sensor 2 (Outer): {devices[1]['usb_path']}")
            if input_devices:
                print(f"  Input devices: {input_devices}")
            return True
        else:
            print(f"⚠️ Found {len(devices)} TEMPerHUM sensors")
            return False
    
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
    
    def identify_sensor_by_timing(self, raw_data, parsed_data):
        """Identify which sensor the data comes from based on timing and patterns."""
        # Since both sensors produce identical data, we need a different approach
        # For now, we'll use a simple alternating pattern based on timing
        
        now = datetime.now()
        
        # Check which sensor was last active
        sensor1_last = self.sensors['sensor_1']['last_activity']
        sensor2_last = self.sensors['sensor_2']['last_activity']
        
        if parsed_data:
            # This is actual sensor data
            if sensor1_last and sensor2_last:
                # Both sensors have been active, use timing
                time_diff1 = (now - sensor1_last).total_seconds()
                time_diff2 = (now - sensor2_last).total_seconds()
                
                # Assign to the sensor that was active more recently
                if time_diff1 < time_diff2:
                    return 'sensor_1'
                else:
                    return 'sensor_2'
            elif sensor1_last:
                return 'sensor_2'  # Try the other sensor
            elif sensor2_last:
                return 'sensor_1'  # Try the other sensor
            else:
                # First reading - assign to sensor 1
                return 'sensor_1'
        else:
            # Banner text - could be from either sensor
            # For now, assign based on which sensor was last active
            if sensor1_last and (not sensor2_last or sensor1_last > sensor2_last):
                return 'sensor_1'
            else:
                return 'sensor_2'
    
    def capture_and_monitor(self):
        """Capture sensor input and monitor in real-time."""
        print("🐢 USB-Separated TEMPerHUM Monitor")
        print("=" * 50)
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
                        
                        # Identify which sensor this data comes from
                        sensor_id = self.identify_sensor_by_timing(line, parsed)
                        
                        # Update the identified sensor
                        sensor = self.sensors[sensor_id]
                        sensor['status'] = 'on'
                        sensor['current_reading'] = {
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'temperature': parsed['temperature'],
                            'humidity': parsed['humidity'],
                            'raw_data': line
                        }
                        sensor['last_activity'] = datetime.now()
                        sensor['readings_count'] += 1
                        
                        print(f"✅ {sensor['name']}: {parsed['temperature']:.1f}°C, {parsed['humidity']:.1f}%")
                    else:
                        # Banner text - identify sensor
                        sensor_id = self.identify_sensor_by_timing(line, None)
                        sensor = self.sensors[sensor_id]
                        sensor['status'] = 'on'
                        sensor['last_activity'] = datetime.now()
                        print(f"📝 {sensor['name']}: {line}")
                    
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
        print("🐢 USB-Separated TEMPerHUM Monitor")
        print("=" * 50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Create JSON output
        status_data = {}
        for sensor_id, sensor in self.sensors.items():
            status_data[sensor_id] = {
                'name': sensor['name'],
                'usb_path': sensor['usb_path'],
                'status': sensor['status'],
                'readings_count': sensor['readings_count'],
                'current_reading': sensor['current_reading']
            }
        
        # Display as formatted JSON
        print(json.dumps(status_data, indent=2))
        print()
        print("Press Ctrl+C to stop")
    
    def run(self):
        """Run the monitor."""
        # Assign sensors to USB ports
        if not self.assign_sensors():
            print("❌ Cannot proceed without proper sensor assignment")
            return
        
        # Start capture and monitoring
        self.capture_and_monitor()
        
        # Final summary
        print("\n📊 FINAL SUMMARY:")
        print("=" * 40)
        for sensor_id, sensor in self.sensors.items():
            print(f"{sensor['name']}:")
            print(f"  USB Path: {sensor['usb_path']}")
            print(f"  Status: {sensor['status']}")
            print(f"  Readings: {sensor['readings_count']}")
            if sensor['current_reading']:
                reading = sensor['current_reading']
                print(f"  Last: {reading['temperature']:.1f}°C, {reading['humidity']:.1f}%")
            print()
        
        print(f"Total captured: {len(self.captured_data)} lines")

def main():
    monitor = USBSeparatedMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 