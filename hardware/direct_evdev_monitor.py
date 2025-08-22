#!/usr/bin/env python3
"""
🐢 Direct EVDEV TEMPerHUM Monitor
==================================
Directly reads from TEMPerHUM input devices using evdev.
Found devices: /dev/input/event3 and /dev/input/event4
"""

import os
import sys
import time
import json
import re
import threading
from datetime import datetime
from evdev import InputDevice, categorize, ecodes

class DirectEvdevMonitor:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1 (Inner)',
                'input_device': '/dev/input/event3',
                'status': 'off',
                'current_reading': None,
                'last_activity': None,
                'readings_count': 0,
                'raw_buffer': ''
            },
            'sensor_2': {
                'name': 'Sensor 2 (Outer)',
                'input_device': '/dev/input/event4',
                'status': 'off',
                'current_reading': None,
                'last_activity': None,
                'readings_count': 0,
                'raw_buffer': ''
            }
        }
        self.running = True
        self.total_readings = 0
        
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
        # Basic keycode to character mapping
        keymap = {
            ecodes.KEY_1: '1', ecodes.KEY_2: '2', ecodes.KEY_3: '3', ecodes.KEY_4: '4',
            ecodes.KEY_5: '5', ecodes.KEY_6: '6', ecodes.KEY_7: '7', ecodes.KEY_8: '8',
            ecodes.KEY_9: '9', ecodes.KEY_0: '0', ecodes.KEY_A: 'a', ecodes.KEY_B: 'b',
            ecodes.KEY_C: 'c', ecodes.KEY_D: 'd', ecodes.KEY_E: 'e', ecodes.KEY_F: 'f',
            ecodes.KEY_G: 'g', ecodes.KEY_H: 'h', ecodes.KEY_I: 'i', ecodes.KEY_J: 'j',
            ecodes.KEY_K: 'k', ecodes.KEY_L: 'l', ecodes.KEY_M: 'm', ecodes.KEY_N: 'n',
            ecodes.KEY_O: 'o', ecodes.KEY_P: 'p', ecodes.KEY_Q: 'q', ecodes.KEY_R: 'r',
            ecodes.KEY_S: 's', ecodes.KEY_T: 't', ecodes.KEY_U: 'u', ecodes.KEY_V: 'v',
            ecodes.KEY_W: 'w', ecodes.KEY_X: 'x', ecodes.KEY_Y: 'y', ecodes.KEY_Z: 'z',
            ecodes.KEY_SPACE: ' ', ecodes.KEY_DOT: '.', ecodes.KEY_MINUS: '-',
            ecodes.KEY_LEFTBRACE: '[', ecodes.KEY_RIGHTBRACE: ']', ecodes.KEY_SLASH: '/',
            ecodes.KEY_PERCENT: '%', ecodes.KEY_EQUAL: '=', ecodes.KEY_COMMA: ',',
            ecodes.KEY_TAB: '\t', ecodes.KEY_ENTER: '\n'
        }
        return keymap.get(keycode, '')
    
    def monitor_sensor(self, sensor_id):
        """Monitor a single sensor's input device"""
        sensor = self.sensors[sensor_id]
        print(f"🔌 Starting monitor for {sensor['name']} at {sensor['input_device']}")
        
        try:
            device = InputDevice(sensor['input_device'])
            print(f"✅ Opened input device: {device.name}")
            
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
                            sensor['raw_buffer'] += char
                            sensor['status'] = 'on'
                            sensor['last_activity'] = datetime.now()
                            
                            # Check if we have a complete line
                            if char == '\n':
                                # Parse the complete line
                                line = sensor['raw_buffer'].strip()
                                sensor['raw_buffer'] = ''
                                
                                if line:
                                    # Try to parse as TEMPerHUM data
                                    parsed = self.parse_temperhum_data(line)
                                    if parsed:
                                        sensor['current_reading'] = parsed
                                        sensor['readings_count'] += 1
                                        self.total_readings += 1
                                        print(f"📊 {sensor['name']}: {parsed['temperature']}°C, {parsed['humidity']}%")
                                    else:
                                        # Might be banner text or other data
                                        print(f"📝 {sensor['name']} raw: {line}")
                        
        except Exception as e:
            print(f"❌ Error in monitor thread for {sensor_id}: {e}")
            sensor['status'] = 'error'
    
    def start_monitoring(self):
        """Start monitoring all sensors"""
        print("\n🐢 Direct EVDEV TEMPerHUM Monitor")
        print("=" * 50)
        print("💡 Activate sensors: Press TXT button or hold Num Lock for 3 seconds")
        print("Press Ctrl+C to stop\n")
        
        # Start monitoring threads for each sensor
        threads = []
        for sensor_id in self.sensors.keys():
            thread = threading.Thread(
                target=self.monitor_sensor,
                args=(sensor_id,)
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
        print("🐢 Direct EVDEV TEMPerHUM Monitor")
        print("=" * 50)
        print(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
        
        status_data = {}
        for sensor_id, sensor in self.sensors.items():
            status_data[sensor_id] = {
                'name': sensor['name'],
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
            print(f"  Input Device: {sensor['input_device']}")
            print(f"  Status: {sensor['status']}")
            print(f"  Readings: {sensor['readings_count']}")
            if sensor['current_reading']:
                reading = sensor['current_reading']
                print(f"  Last: {reading['temperature']}°C, {reading['humidity']}%")
            print()
        print(f"Total Readings: {self.total_readings}")

def main():
    monitor = DirectEvdevMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main() 