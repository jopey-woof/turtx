#!/usr/bin/env python3
"""
🐢 EVDEV TEMPerHUM Sensor Monitor
==================================
Uses evdev to directly read from each sensor's input device file,
allowing us to distinguish between sensors on different USB ports.
"""

import os
import sys
import time
import json
import re
import threading
from datetime import datetime
import subprocess
from evdev import InputDevice, categorize, ecodes

class EvdevSensorMonitor:
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
        self.total_readings = 0
        
    def find_temperhum_devices(self):
        """Find TEMPerHUM devices and their USB paths"""
        print("🔍 Finding TEMPerHUM devices...")
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            devices = []
            for line in result.stdout.split('\n'):
                if 'TEMPerHUM' in line:
                    print(f"✅ Found: {line.strip()}")
                    # Extract bus and device numbers
                    match = re.search(r'Bus (\d+) Device (\d+):', line)
                    if match:
                        bus = match.group(1)
                        device = match.group(2)
                        usb_path = f"/dev/bus/usb/{bus.zfill(3)}/{device.zfill(3)}"
                        devices.append(usb_path)
            
            print(f"📊 Found {len(devices)} TEMPerHUM device(s)")
            return devices
        except Exception as e:
            print(f"❌ Error finding devices: {e}")
            return []
    
    def find_input_devices(self, usb_paths):
        """Find input device files for each USB device"""
        print("🔍 Finding input devices...")
        input_devices = {}
        
        try:
            # Get all input devices
            result = subprocess.run(['ls', '/dev/input/event*'], capture_output=True, text=True)
            event_devices = result.stdout.strip().split('\n')
            
            for usb_path in usb_paths:
                # Get device info for this USB path
                try:
                    result = subprocess.run(['udevadm', 'info', '--query=property', usb_path], 
                                          capture_output=True, text=True)
                    device_props = result.stdout
                    
                    # Find matching input device
                    for event_device in event_devices:
                        if not event_device:
                            continue
                            
                        # Get properties of this input device
                        try:
                            result = subprocess.run(['udevadm', 'info', '--query=property', event_device], 
                                                  capture_output=True, text=True)
                            input_props = result.stdout
                            
                            # Check if this input device belongs to our USB device
                            # Look for matching vendor/product IDs or device paths
                            if any(prop in input_props for prop in ['ID_VENDOR_ID=3553', 'ID_MODEL_ID=a001']):
                                print(f"✅ Found input device {event_device} for {usb_path}")
                                input_devices[usb_path] = event_device
                                break
                        except:
                            continue
                            
                except Exception as e:
                    print(f"❌ Error getting device info for {usb_path}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error finding input devices: {e}")
            
        return input_devices
    
    def parse_temperhum_data(self, raw_data):
        """Parse TEMPerHUM data format: 29.16 [c]36.08 [%rh]1s"""
        pattern = r'(\d+\.?\d*)\s*\[c\](\d+\.?\d*)\s*\[%rh\](\d+)s'
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
                    'raw_data': raw_data
                }
            except (ValueError, IndexError):
                pass
        return None
    
    def read_sensor_data(self, sensor_id, input_device_path):
        """Read data from a specific sensor's input device"""
        sensor = self.sensors[sensor_id]
        print(f"🔌 Starting to read from {sensor['name']} at {input_device_path}")
        
        try:
            device = InputDevice(input_device_path)
            print(f"✅ Opened input device: {device.name}")
            
            # Read events from this device
            for event in device.read_loop():
                if not self.running:
                    break
                    
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        # This is a key press - could be part of sensor data
                        # We need to collect the full string
                        pass
                        
        except Exception as e:
            print(f"❌ Error reading from {input_device_path}: {e}")
    
    def monitor_sensor_thread(self, sensor_id, input_device_path):
        """Monitor a single sensor in a separate thread"""
        sensor = self.sensors[sensor_id]
        print(f"🔌 Starting monitor for {sensor['name']} at {input_device_path}")
        
        try:
            device = InputDevice(input_device_path)
            print(f"✅ Opened input device: {device.name}")
            
            # Read events from this device
            for event in device.read_loop():
                if not self.running:
                    break
                    
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        # This is a key press - could be part of sensor data
                        # We need to collect the full string
                        pass
                        
        except Exception as e:
            print(f"❌ Error in monitor thread for {sensor_id}: {e}")
    
    def setup_sensors(self):
        """Setup sensors with their USB paths and input devices"""
        usb_paths = self.find_temperhum_devices()
        if len(usb_paths) < 2:
            print("❌ Need at least 2 TEMPerHUM devices")
            return False
            
        input_devices = self.find_input_devices(usb_paths)
        if len(input_devices) < 2:
            print("❌ Could not find input devices for both sensors")
            return False
            
        # Assign USB paths and input devices to sensors
        sensor_keys = list(self.sensors.keys())
        for i, (usb_path, input_device) in enumerate(input_devices.items()):
            if i < len(sensor_keys):
                sensor_id = sensor_keys[i]
                self.sensors[sensor_id]['usb_path'] = usb_path
                self.sensors[sensor_id]['input_device'] = input_device
                print(f"🔌 {self.sensors[sensor_id]['name']}: {usb_path} -> {input_device}")
                
        return True
    
    def start_monitoring(self):
        """Start monitoring all sensors"""
        if not self.setup_sensors():
            return
            
        print("\n🐢 EVDEV TEMPerHUM Sensor Monitor")
        print("=" * 50)
        print("💡 Activate sensors: Press TXT button or hold Num Lock for 3 seconds")
        print("Press Ctrl+C to stop\n")
        
        # Start monitoring threads for each sensor
        threads = []
        for sensor_id, sensor in self.sensors.items():
            if sensor['input_device']:
                thread = threading.Thread(
                    target=self.monitor_sensor_thread,
                    args=(sensor_id, sensor['input_device'])
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)
        
        # Main display loop
        try:
            while self.running:
                self.display_status()
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("\n🛑 Stopping monitor...")
            
        # Wait for threads to finish
        for thread in threads:
            thread.join(timeout=1)
            
        self.display_final_summary()
    
    def display_status(self):
        """Display current sensor status"""
        os.system('clear')
        print("🐢 EVDEV TEMPerHUM Sensor Monitor")
        print("=" * 50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        status_data = {}
        for sensor_id, sensor in self.sensors.items():
            status_data[sensor_id] = {
                'name': sensor['name'],
                'usb_path': sensor['usb_path'],
                'input_device': sensor['input_device'],
                'status': sensor['status'],
                'readings_count': sensor['readings_count'],
                'current_reading': sensor['current_reading']
            }
        
        print(json.dumps(status_data, indent=2))
        print("\nPress Ctrl+C to stop")
    
    def display_final_summary(self):
        """Display final summary when stopping"""
        print("\n📊 FINAL SUMMARY:")
        print("=" * 40)
        for sensor_id, sensor in self.sensors.items():
            print(f"{sensor['name']}:")
            print(f"  USB Path: {sensor['usb_path']}")
            print(f"  Input Device: {sensor['input_device']}")
            print(f"  Status: {sensor['status']}")
            print(f"  Readings: {sensor['readings_count']}")
            if sensor['current_reading']:
                reading = sensor['current_reading']
                print(f"  Last: {reading['temperature']}°C, {reading['humidity']}%")
            print()
        print(f"Total Readings: {self.total_readings}")

def main():
    monitor = EvdevSensorMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main() 