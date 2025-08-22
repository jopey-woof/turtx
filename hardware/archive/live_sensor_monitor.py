#!/usr/bin/env python3
"""
Live TemperhUM Sensor Monitor - Interactive data capture with proper handling
"""
import evdev
import time
import threading
import signal
import sys
from queue import Queue, Empty
import re

class LiveSensorMonitor:
    def __init__(self):
        self.running = True
        self.data_queue = Queue()
        self.line_buffers = {}
        self.sensor_data = {}
        
    def signal_handler(self, sig, frame):
        print("\n🛑 Stopping monitor...")
        self.running = False
        
    def find_sensors(self):
        """Find TemperhUM input devices"""
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            temperhum_devices = [d for d in devices if "TEMPerHUM" in d.name]
            return temperhum_devices
        except Exception as e:
            print(f"Error finding sensors: {e}")
            return []
    
    def listen_device(self, device):
        """Listen to a single device with proper error handling"""
        keycode_map = {
            evdev.ecodes.KEY_1: '1', evdev.ecodes.KEY_2: '2', evdev.ecodes.KEY_3: '3',
            evdev.ecodes.KEY_4: '4', evdev.ecodes.KEY_5: '5', evdev.ecodes.KEY_6: '6',
            evdev.ecodes.KEY_7: '7', evdev.ecodes.KEY_8: '8', evdev.ecodes.KEY_9: '9',
            evdev.ecodes.KEY_0: '0', evdev.ecodes.KEY_DOT: '.', 
            evdev.ecodes.KEY_LEFTBRACE: '[', evdev.ecodes.KEY_RIGHTBRACE: ']',
            evdev.ecodes.KEY_C: 'C', evdev.ecodes.KEY_H: 'H', evdev.ecodes.KEY_R: 'R',
            evdev.ecodes.KEY_S: 'S', evdev.ecodes.KEY_ENTER: '\n', evdev.ecodes.KEY_SPACE: ' ',
            evdev.ecodes.KEY_COMMA: ',', evdev.ecodes.KEY_SEMICOLON: ';',
            evdev.ecodes.KEY_APOSTROPHE: "'", evdev.ecodes.KEY_SLASH: '/',
            evdev.ecodes.KEY_BACKSLASH: '\\', evdev.ecodes.KEY_MINUS: '-',
            evdev.ecodes.KEY_EQUAL: '=', evdev.ecodes.KEY_GRAVE: '`',
            evdev.ecodes.KEY_A: 'A', evdev.ecodes.KEY_B: 'B', evdev.ecodes.KEY_D: 'D',
            evdev.ecodes.KEY_E: 'E', evdev.ecodes.KEY_F: 'F', evdev.ecodes.KEY_G: 'G',
            evdev.ecodes.KEY_I: 'I', evdev.ecodes.KEY_J: 'J', evdev.ecodes.KEY_K: 'K',
            evdev.ecodes.KEY_L: 'L', evdev.ecodes.KEY_M: 'M', evdev.ecodes.KEY_N: 'N',
            evdev.ecodes.KEY_O: 'O', evdev.ecodes.KEY_P: 'P', evdev.ecodes.KEY_Q: 'Q',
            evdev.ecodes.KEY_T: 'T', evdev.ecodes.KEY_U: 'U', evdev.ecodes.KEY_V: 'V',
            evdev.ecodes.KEY_W: 'W', evdev.ecodes.KEY_X: 'X', evdev.ecodes.KEY_Y: 'Y',
            evdev.ecodes.KEY_Z: 'Z'
        }
        
        device_name = f"{device.path}({device.phys})"
        
        try:
            for event in device.read_loop():
                if not self.running:
                    break
                    
                if event.type == evdev.ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    if key_event.keystate == key_event.key_down:
                        char = keycode_map.get(key_event.scancode)
                        if char:
                            self.data_queue.put((device_name, char))
                            
        except Exception as e:
            if self.running:  # Only report errors if we're still supposed to be running
                print(f"Device listener error for {device_name}: {e}")
    
    def parse_sensor_line(self, line, source):
        """Parse sensor data line"""
        line = line.strip()
        
        # Skip empty lines
        if not line:
            return None
            
        # Check for temperature/humidity data
        temp_humid_match = re.match(r"(\d+\.\d+)\s*\[C\]\s*(\d+\.\d+)\s*\[[%5]RH\]\s*(\d+)S", line)
        if temp_humid_match:
            temp = float(temp_humid_match.group(1))
            humidity = float(temp_humid_match.group(2))
            interval = int(temp_humid_match.group(3))
            
            # Store sensor data
            sensor_id = f"sensor_{interval}s"
            self.sensor_data[sensor_id] = {
                'temperature': temp,
                'humidity': humidity,
                'interval': interval,
                'source': source,
                'timestamp': time.time()
            }
            
            return {
                'type': 'data',
                'temperature': temp,
                'humidity': humidity,
                'interval': interval,
                'sensor_id': sensor_id
            }
        
        # Check for banner/info text
        if any(keyword in line.upper() for keyword in ['TEMPERHUM', 'PCSENSOR', 'WWW.', 'CAPS LOCK', 'NUM LOCK', 'TYPE:', 'INNER-']):
            return {'type': 'banner', 'content': line}
        
        # Unknown format
        return {'type': 'unknown', 'content': line}
    
    def display_status(self):
        """Display current sensor status"""
        if self.sensor_data:
            print(f"\n📊 CURRENT SENSOR DATA:")
            print("-" * 50)
            for sensor_id, data in self.sensor_data.items():
                age = time.time() - data['timestamp']
                print(f"{sensor_id.upper()}: {data['temperature']}°C, {data['humidity']}% RH ({age:.1f}s ago)")
            print("-" * 50)
    
    def run_monitor(self):
        """Run the interactive sensor monitor"""
        print("🔴 LIVE TEMPERHUM SENSOR MONITOR")
        print("=" * 45)
        print("Monitoring sensor data in real-time...")
        print("Press Ctrl+C to stop")
        print()
        
        # Set up signal handling for clean exit
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Find sensors
        sensors = self.find_sensors()
        if not sensors:
            print("❌ No TemperhUM sensors found!")
            return
        
        print(f"📡 Found {len(sensors)} sensor interfaces:")
        for i, sensor in enumerate(sensors, 1):
            print(f"  {i}. {sensor.path} - {sensor.phys}")
        print()
        
        # Start listeners
        threads = []
        for sensor in sensors:
            thread = threading.Thread(
                target=self.listen_device, 
                args=(sensor,), 
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        print("🎯 LIVE DATA (press Ctrl+C to stop):")
        print("=" * 45)
        
        last_status_time = 0
        
        # Main monitoring loop
        while self.running:
            try:
                # Get data with timeout
                try:
                    device_name, char = self.data_queue.get(timeout=1.0)
                except Empty:
                    # Show status every 10 seconds if no data
                    if time.time() - last_status_time > 10:
                        if self.sensor_data:
                            self.display_status()
                        else:
                            print("⏳ Waiting for sensor data... (try pressing Caps Lock on sensors)")
                        last_status_time = time.time()
                    continue
                
                # Handle line buffering per device
                if device_name not in self.line_buffers:
                    self.line_buffers[device_name] = ""
                
                if char == '\n':
                    # Process complete line
                    if self.line_buffers[device_name]:
                        line = self.line_buffers[device_name]
                        timestamp = time.strftime("%H:%M:%S")
                        
                        # Parse the line
                        parsed = self.parse_sensor_line(line, device_name)
                        
                        if parsed:
                            if parsed['type'] == 'data':
                                print(f"[{timestamp}] 📊 {parsed['sensor_id'].upper()}: {parsed['temperature']}°C, {parsed['humidity']}% RH")
                            elif parsed['type'] == 'banner':
                                print(f"[{timestamp}] 🏷️  BANNER: {parsed['content']}")
                            elif parsed['type'] == 'unknown':
                                print(f"[{timestamp}] ❓ UNKNOWN: {parsed['content']}")
                        
                        self.line_buffers[device_name] = ""
                else:
                    # Add character to buffer
                    self.line_buffers[device_name] += char
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                continue
        
        print(f"\n✅ Monitor stopped.")
        
        # Final status
        if self.sensor_data:
            print(f"\n📋 FINAL SENSOR SUMMARY:")
            print("-" * 30)
            for sensor_id, data in self.sensor_data.items():
                print(f"{sensor_id.upper()}: {data['temperature']}°C, {data['humidity']}% RH")
                print(f"  Interval: {data['interval']}s, Source: {data['source']}")

def main():
    monitor = LiveSensorMonitor()
    monitor.run_monitor()

if __name__ == "__main__":
    main()