#!/usr/bin/env python3
"""
🐢 Auto-Detect TEMPerHUM Monitor
=================================
Automatically detects which sensor is being used when you press the button.
Run with: sudo python3 auto_detect_monitor.py
"""

import os
import sys
import time
import json
import re
import threading
from datetime import datetime
from evdev import InputDevice, categorize, ecodes

class AutoDetectMonitor:
    def __init__(self):
        self.sensors = {}
        self.running = True
        self.total_readings = 0
        self.lock = threading.Lock()
        
    def find_temperhum_devices(self):
        """Find all TEMPerHUM input devices"""
        devices = []
        try:
            # Get all input devices
            result = os.popen('ls /dev/input/event*').read().strip().split('\n')
            
            for device_path in result:
                if not device_path:
                    continue
                    
                try:
                    # Get device info
                    result = os.popen(f'udevadm info --query=property {device_path}').read()
                    if 'ID_MODEL=TEMPerHUM' in result:
                        devices.append(device_path)
                        print(f"✅ Found TEMPerHUM device: {device_path}")
                except:
                    continue
                    
        except Exception as e:
            print(f"❌ Error finding devices: {e}")
            
        return devices
    
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
                    'raw_data': raw_data,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                }
            except (ValueError, IndexError):
                pass
        return None
    
    def keycode_to_char(self, keycode):
        """Convert evdev keycode to character"""
        keymap = {
            2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
            16: 'q', 17: 'w', 18: 'e', 19: 'r', 20: 't', 21: 'y', 22: 'u', 23: 'i', 24: 'o', 25: 'p',
            30: 'a', 31: 's', 32: 'd', 33: 'f', 34: 'g', 35: 'h', 36: 'j', 37: 'k', 38: 'l',
            44: 'z', 45: 'x', 46: 'c', 47: 'v', 48: 'b', 49: 'n', 50: 'm',
            57: ' ', 52: '.', 12: '-', 26: '[', 27: ']', 53: '/', 15: '\t', 28: '\n',
        }
        return keymap.get(keycode, '')
    
    def identify_sensor_from_banner(self, banner_text):
        """Identify sensor type from banner text"""
        if 'inner-temp' in banner_text.lower() or 'inner-hum' in banner_text.lower():
            return 'Inner Sensor'
        elif 'outer-temp' in banner_text.lower() or 'outer-hum' in banner_text.lower():
            return 'Outer Sensor'
        else:
            return 'Unknown Sensor'
    
    def monitor_device(self, device_path):
        """Monitor a single device"""
        sensor_id = device_path.split('/')[-1]  # Use event name as ID
        
        with self.lock:
            self.sensors[sensor_id] = {
                'device_path': device_path,
                'name': f'Sensor {sensor_id}',
                'status': 'off',
                'current_reading': None,
                'last_activity': None,
                'readings_count': 0,
                'raw_buffer': '',
                'identified': False
            }
        
        print(f"🔌 Starting monitor for {device_path}")
        
        try:
            device = InputDevice(device_path)
            print(f"✅ Opened device: {device.name}")
            
            # Read events from this device
            for event in device.read_loop():
                if not self.running:
                    break
                    
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        # Convert keycode to character
                        char = self.keycode_to_char(key_event.keycode)
                        if char:
                            with self.lock:
                                self.sensors[sensor_id]['raw_buffer'] += char
                                self.sensors[sensor_id]['status'] = 'on'
                                self.sensors[sensor_id]['last_activity'] = datetime.now()
                            
                            # Check if we have a complete line
                            if char == '\n':
                                with self.lock:
                                    # Parse the complete line
                                    line = self.sensors[sensor_id]['raw_buffer'].strip()
                                    self.sensors[sensor_id]['raw_buffer'] = ''
                                
                                if line:
                                    print(f"📝 {device_path} raw: '{line}'")
                                    
                                    # Try to parse as TEMPerHUM data
                                    parsed = self.parse_temperhum_data(line)
                                    if parsed:
                                        with self.lock:
                                            self.sensors[sensor_id]['current_reading'] = parsed
                                            self.sensors[sensor_id]['readings_count'] += 1
                                            self.total_readings += 1
                                        print(f"📊 {device_path}: {parsed['temperature']}°C, {parsed['humidity']}%")
                                    else:
                                        # Check if this is banner text for identification
                                        if not self.sensors[sensor_id]['identified']:
                                            sensor_name = self.identify_sensor_from_banner(line)
                                            if sensor_name != 'Unknown Sensor':
                                                with self.lock:
                                                    self.sensors[sensor_id]['name'] = sensor_name
                                                    self.sensors[sensor_id]['identified'] = True
                                                print(f"🏷️ {device_path} identified as: {sensor_name}")
                        
        except Exception as e:
            print(f"❌ Error monitoring {device_path}: {e}")
            with self.lock:
                self.sensors[sensor_id]['status'] = 'error'
    
    def start_monitoring(self):
        """Start monitoring all detected sensors"""
        print("\n🐢 Auto-Detect TEMPerHUM Monitor")
        print("=" * 50)
        print("💡 Press TXT button on any sensor to activate it")
        print("Press Ctrl+C to stop\n")
        
        # Find all TEMPerHUM devices
        devices = self.find_temperhum_devices()
        if not devices:
            print("❌ No TEMPerHUM devices found")
            return
        
        print(f"📊 Found {len(devices)} TEMPerHUM device(s)")
        
        # Start monitoring threads for each device
        threads = []
        for device_path in devices:
            thread = threading.Thread(
                target=self.monitor_device,
                args=(device_path,)
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
            thread.join(timeout=2)
            
        self.display_final_summary()
    
    def display_status(self):
        """Display current sensor status"""
        os.system('clear')
        print("🐢 Auto-Detect TEMPerHUM Monitor")
        print("=" * 50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        with self.lock:
            status_data = {}
            for sensor_id, sensor in self.sensors.items():
                status_data[sensor_id] = {
                    'name': sensor['name'],
                    'device_path': sensor['device_path'],
                    'status': sensor['status'],
                    'readings_count': sensor['readings_count'],
                    'current_reading': sensor['current_reading'],
                    'identified': sensor['identified']
                }
        
        print(json.dumps(status_data, indent=2))
        print("\nPress Ctrl+C to stop")
    
    def display_final_summary(self):
        """Display final summary when stopping"""
        print("\n📊 FINAL SUMMARY:")
        print("=" * 40)
        with self.lock:
            for sensor_id, sensor in self.sensors.items():
                print(f"{sensor['name']}:")
                print(f"  Device: {sensor['device_path']}")
                print(f"  Status: {sensor['status']}")
                print(f"  Readings: {sensor['readings_count']}")
                if sensor['current_reading']:
                    reading = sensor['current_reading']
                    print(f"  Last: {reading['temperature']}°C, {reading['humidity']}%")
                print()
            print(f"Total Readings: {self.total_readings}")

def main():
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script must be run with sudo")
        print("Run: sudo python3 auto_detect_monitor.py")
        sys.exit(1)
        
    monitor = AutoDetectMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main() 