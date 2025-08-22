#!/usr/bin/env python3
"""
🐢 Working TEMPerHUM Monitor
=============================
Focuses on the working device and captures sensor data properly.
Run with: sudo python3 working_monitor.py
"""

import os
import sys
import time
import json
import re
from datetime import datetime
from evdev import InputDevice, categorize, ecodes

class WorkingMonitor:
    def __init__(self):
        self.device_path = "/dev/input/event25"  # The working device
        self.sensor_name = "Active Sensor"
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
        """Convert evdev keycode to character - comprehensive mapping"""
        # Comprehensive keycode mapping
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
            57: ' ',  # space
            52: '.',  # dot
            12: '-',  # minus
            26: '[',  # left brace
            27: ']',  # right brace
            53: '/',  # slash
            15: '\t', # tab
            28: '\n', # enter
            # Additional characters that might be used
            13: '=',  # equal
            39: ';',  # semicolon
            40: "'",  # apostrophe
            41: '`',  # backtick
            43: '\\', # backslash
            51: ',',  # comma
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
    
    def monitor_sensor(self):
        """Monitor the sensor's input device"""
        print(f"🔌 Starting monitor for {self.sensor_name} at {self.device_path}")
        
        try:
            device = InputDevice(self.device_path)
            print(f"✅ Opened device: {device.name}")
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
                            
                            # Debug: print key events (only first few)
                            if len(self.raw_buffer) < 50:
                                print(f"🔤 Key: {key_event.keycode} -> '{char}' (buffer: '{self.raw_buffer}')")
                            
                            # Check if we have a complete line
                            if char == '\n':
                                # Parse the complete line
                                line = self.raw_buffer.strip()
                                self.raw_buffer = ''
                                
                                if line:
                                    print(f"📝 Complete line: '{line}'")
                                    
                                    # Try to parse as TEMPerHUM data
                                    parsed = self.parse_temperhum_data(line)
                                    if parsed:
                                        self.current_reading = parsed
                                        self.readings_count += 1
                                        print(f"📊 {self.sensor_name}: {parsed['temperature']}°C, {parsed['humidity']}%")
                                        self.display_status()
                                    else:
                                        # Check if this is banner text for identification
                                        sensor_name = self.identify_sensor_from_banner(line)
                                        if sensor_name != 'Unknown Sensor':
                                            self.sensor_name = sensor_name
                                            print(f"🏷️ Sensor identified as: {sensor_name}")
                        
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
            'device_path': self.device_path,
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
        print(f"  Device: {self.device_path}")
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
        print("Run: sudo python3 working_monitor.py")
        sys.exit(1)
    
    print("\n🐢 Working TEMPerHUM Monitor")
    print("=" * 50)
    print("💡 Press TXT button on the sensor to activate it")
    print("Press Ctrl+C to stop\n")
    
    monitor = WorkingMonitor()
    
    try:
        monitor.monitor_sensor()
    except KeyboardInterrupt:
        monitor.running = False
        print("\n🛑 Stopping monitor...")
        monitor.display_final_summary()

if __name__ == "__main__":
    main() 