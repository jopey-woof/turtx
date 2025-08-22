#!/usr/bin/env python3
"""
🐢 Device-Separate TEMPerHUM Capture
=====================================
Monitors each TEMPerHUM input device separately and captures to separate files.
Run with: sudo python3 device_separate_capture.py
"""

import os
import sys
import time
import json
import re
import threading
from datetime import datetime
from evdev import InputDevice, categorize, ecodes

class DeviceSeparateCapture:
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
    
    def keycode_to_char(self, keycode):
        """Convert evdev keycode to character"""
        keymap = {
            # Numbers
            2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
            # Letters - first row
            16: 'q', 17: 'w', 18: 'e', 19: 'r', 20: 't', 21: 'y', 22: 'u', 23: 'i', 24: 'o', 25: 'p',
            # Letters - second row
            30: 'a', 31: 's', 32: 'd', 33: 'f', 34: 'g', 35: 'h', 36: 'j', 37: 'k', 38: 'l',
            # Letters - third row
            44: 'z', 45: 'x', 46: 'c', 47: 'v', 48: 'b', 49: 'n', 50: 'm',
            # Special characters
            57: ' ', 52: '.', 12: '-', 26: '[', 27: ']', 53: '/', 15: '\t', 28: '\n',
            # Additional characters
            13: '=', 39: ';', 40: "'", 41: '`', 43: '\\', 51: ',',
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
        """Monitor a single device and capture to separate file"""
        sensor_id = device_path.split('/')[-1]  # Use event name as ID
        output_file = f"/tmp/sensor_{sensor_id}.txt"
        
        with self.lock:
            self.sensors[sensor_id] = {
                'device_path': device_path,
                'name': f'Sensor {sensor_id}',
                'output_file': output_file,
                'status': 'off',
                'current_reading': None,
                'last_activity': None,
                'readings_count': 0,
                'raw_buffer': '',
                'identified': False
            }
        
        print(f"🔌 Starting monitor for {device_path} -> {output_file}")
        
        try:
            device = InputDevice(device_path)
            print(f"✅ Opened device: {device.name}")
            
            # Open output file for this sensor
            with open(output_file, 'w') as f:
                f.write(f"# TEMPerHUM Sensor {sensor_id} Output\n")
                f.write(f"# Started: {datetime.now()}\n")
                f.write("# Format: timestamp, temperature, humidity, raw_data\n\n")
            
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
                                    # Write to sensor-specific file
                                    timestamp = datetime.now().strftime('%H:%M:%S')
                                    with open(output_file, 'a') as f:
                                        f.write(f"{timestamp}: {line}\n")
                                    
                                    print(f"📝 {device_path} -> {output_file}: '{line}'")
                                    
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
            import traceback
            traceback.print_exc()
            with self.lock:
                self.sensors[sensor_id]['status'] = 'error'
    
    def start_monitoring(self):
        """Start monitoring all detected sensors"""
        print("\n🐢 Device-Separate TEMPerHUM Capture")
        print("=" * 50)
        print("💡 Press TXT button on sensors to activate them")
        print("Each sensor output goes to separate file in /tmp/")
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
        print("🐢 Device-Separate TEMPerHUM Capture")
        print("=" * 50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        with self.lock:
            status_data = {}
            for sensor_id, sensor in self.sensors.items():
                status_data[sensor_id] = {
                    'name': sensor['name'],
                    'device_path': sensor['device_path'],
                    'output_file': sensor['output_file'],
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
                print(f"  Output File: {sensor['output_file']}")
                print(f"  Status: {sensor['status']}")
                print(f"  Readings: {sensor['readings_count']}")
                if sensor['current_reading']:
                    reading = sensor['current_reading']
                    print(f"  Last: {reading['temperature']}°C, {reading['humidity']}%")
                print()
            print(f"Total Readings: {self.total_readings}")
        
        print("\n📁 Output files:")
        for sensor_id, sensor in self.sensors.items():
            if os.path.exists(sensor['output_file']):
                size = os.path.getsize(sensor['output_file'])
                print(f"  {sensor['output_file']}: {size} bytes")

def main():
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script must be run with sudo")
        print("Run: sudo python3 device_separate_capture.py")
        sys.exit(1)
        
    monitor = DeviceSeparateCapture()
    monitor.start_monitoring()

if __name__ == "__main__":
    main() 