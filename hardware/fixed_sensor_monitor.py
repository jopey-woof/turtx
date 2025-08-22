#!/usr/bin/env python3
"""
🐢 Fixed Sensor Monitor
=======================
Fixed version that properly captures TEMPerHUM sensor data.
Run with: sudo python3 fixed_sensor_monitor.py
"""

import os
import sys
import time
import json
import re
from datetime import datetime
from evdev import InputDevice, categorize, ecodes

class FixedSensorMonitor:
    def __init__(self, device_path, sensor_name):
        self.device_path = device_path
        self.sensor_name = sensor_name
        self.status = 'off'
        self.current_reading = None
        self.last_activity = None
        self.readings_count = 0
        self.raw_buffer = ''
        self.running = True
        
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
        """Convert evdev keycode to character - fixed mapping"""
        # Fixed keycode to character mapping based on actual evdev codes
        keymap = {
            2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 11: '0',
            16: 'q', 17: 'w', 18: 'e', 19: 'r', 20: 't', 21: 'y', 22: 'u', 23: 'i', 24: 'o', 25: 'p',
            30: 'a', 31: 's', 32: 'd', 33: 'f', 34: 'g', 35: 'h', 36: 'j', 37: 'k', 38: 'l',
            44: 'z', 45: 'x', 46: 'c', 47: 'v', 48: 'b', 49: 'n', 50: 'm',
            57: ' ',  # space
            52: '.',  # dot
            12: '-',  # minus
            26: '[',  # left brace
            27: ']',  # right brace
            53: '/',  # slash
            15: '\t', # tab
            28: '\n', # enter
        }
        return keymap.get(keycode, '')
    
    def monitor_sensor(self):
        """Monitor the sensor's input device"""
        print(f"🔌 Starting monitor for {self.sensor_name} at {self.device_path}")
        
        try:
            device = InputDevice(self.device_path)
            print(f"✅ Opened input device: {device.name}")
            print(f"📋 Device info: {device.info}")
            
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
                            self.raw_buffer += char
                            self.status = 'on'
                            self.last_activity = datetime.now()
                            
                            # Debug: print key events
                            print(f"🔤 Key: {key_event.keycode} -> '{char}' (buffer: '{self.raw_buffer}')")
                            
                            # Check if we have a complete line
                            if char == '\n':
                                # Parse the complete line
                                line = self.raw_buffer.strip()
                                self.raw_buffer = ''
                                
                                if line:
                                    print(f"📝 {self.sensor_name} complete line: '{line}'")
                                    
                                    # Try to parse as TEMPerHUM data
                                    parsed = self.parse_temperhum_data(line)
                                    if parsed:
                                        self.current_reading = parsed
                                        self.readings_count += 1
                                        print(f"📊 {self.sensor_name}: {parsed['temperature']}°C, {parsed['humidity']}%")
                                        self.display_status()
                        
        except Exception as e:
            print(f"❌ Error in monitor: {e}")
            import traceback
            traceback.print_exc()
            self.status = 'error'
    
    def display_status(self):
        """Display current sensor status"""
        os.system('clear')
        print(f"🐢 {self.sensor_name} Monitor")
        print("=" * 50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        status_data = {
            'name': self.sensor_name,
            'input_device': self.device_path,
            'status': self.status,
            'readings_count': self.readings_count,
            'current_reading': self.current_reading
        }
        
        print(json.dumps(status_data, indent=2))
        print("\nPress Ctrl+C to stop")
    
    def display_final_summary(self):
        """Display final summary when stopping"""
        print("\n📊 FINAL SUMMARY:")
        print("=" * 40)
        print(f"{self.sensor_name}:")
        print(f"  Input Device: {self.device_path}")
        print(f"  Status: {self.status}")
        print(f"  Readings: {self.readings_count}")
        if self.current_reading:
            reading = self.current_reading
            print(f"  Last: {reading['temperature']}°C, {reading['humidity']}%")
        print()

def main():
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script must be run with sudo")
        print("Run: sudo python3 fixed_sensor_monitor.py")
        sys.exit(1)
    
    # Choose which sensor to monitor
    print("🐢 Fixed Sensor TEMPerHUM Monitor")
    print("=" * 40)
    print("1. Monitor Sensor 1 (/dev/input/event3)")
    print("2. Monitor Sensor 2 (/dev/input/event4)")
    
    choice = input("Choose sensor (1 or 2): ").strip()
    
    if choice == "1":
        device_path = "/dev/input/event3"
        sensor_name = "Sensor 1"
    elif choice == "2":
        device_path = "/dev/input/event4"
        sensor_name = "Sensor 2"
    else:
        print("Invalid choice. Using Sensor 1.")
        device_path = "/dev/input/event3"
        sensor_name = "Sensor 1"
    
    print(f"\n🔌 Monitoring {sensor_name} at {device_path}")
    print("💡 Activate sensor: Press TXT button or hold Num Lock for 3 seconds")
    print("Press Ctrl+C to stop\n")
    
    monitor = FixedSensorMonitor(device_path, sensor_name)
    
    try:
        monitor.monitor_sensor()
    except KeyboardInterrupt:
        monitor.running = False
        print("\n🛑 Stopping monitor...")
        monitor.display_final_summary()

if __name__ == "__main__":
    main() 