#!/usr/bin/env python3
"""
Manual TemperhUM Test - Wait for manual activation and capture data
"""
import evdev
import time
import threading
from queue import Queue, Empty
import signal
import sys

class ManualTest:
    def __init__(self):
        self.running = True
        
    def signal_handler(self, sig, frame):
        print("\n🛑 Stopping test...")
        self.running = False
        
    def find_temperhum_keyboards(self):
        """Find TemperhUM keyboard interfaces"""
        try:
            evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            temperhum_keyboards = [d for d in evdev_devices if "TEMPerHUM" in d.name]
            return temperhum_keyboards
        except Exception as e:
            print(f"Error finding keyboards: {e}")
            return []
    
    def monitor_manual_activation(self):
        """Monitor for manual sensor activation"""
        print("🎯 MANUAL TEMPERHUM TEST")
        print("=" * 30)
        print("Please MANUALLY press and hold Caps Lock on a sensor for 1 second")
        print("Press Ctrl+C to exit")
        print()
        
        signal.signal(signal.SIGINT, self.signal_handler)
        
        check_interval = 2  # Check every 2 seconds
        last_keyboard_count = 0
        
        while self.running:
            try:
                keyboards = self.find_temperhum_keyboards()
                current_count = len(keyboards)
                
                if current_count != last_keyboard_count:
                    print(f"📋 Keyboard interfaces: {current_count}")
                    for kbd in keyboards:
                        print(f"  {kbd.path}: {kbd.name}")
                    last_keyboard_count = current_count
                
                if keyboards and current_count > 0:
                    print("\n🎉 TemperhUM keyboard found! Monitoring data...")
                    self.monitor_data(keyboards)
                    break
                
                # Wait and check again
                time.sleep(check_interval)
                print(".", end="", flush=True)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
        
        print("\nTest ended")
    
    def monitor_data(self, keyboards):
        """Monitor data from keyboards"""
        keycode_map = {
            evdev.ecodes.KEY_1: '1', evdev.ecodes.KEY_2: '2', evdev.ecodes.KEY_3: '3',
            evdev.ecodes.KEY_4: '4', evdev.ecodes.KEY_5: '5', evdev.ecodes.KEY_6: '6',
            evdev.ecodes.KEY_7: '7', evdev.ecodes.KEY_8: '8', evdev.ecodes.KEY_9: '9',
            evdev.ecodes.KEY_0: '0', evdev.ecodes.KEY_DOT: '.', 
            evdev.ecodes.KEY_LEFTBRACE: '[', evdev.ecodes.KEY_RIGHTBRACE: ']',
            evdev.ecodes.KEY_C: 'C', evdev.ecodes.KEY_H: 'H', evdev.ecodes.KEY_R: 'R',
            evdev.ecodes.KEY_S: 'S', evdev.ecodes.KEY_ENTER: '\n', evdev.ecodes.KEY_SPACE: ' '
        }
        
        data_queue = Queue()
        
        def listen_device(device):
            try:
                print(f"📡 Listening on {device.path}")
                for event in device.read_loop():
                    if not self.running:
                        break
                    if event.type == evdev.ecodes.EV_KEY:
                        key_event = evdev.categorize(event)
                        if key_event.keystate == key_event.key_down:
                            char = keycode_map.get(key_event.scancode)
                            if char:
                                data_queue.put((device.path, char))
            except Exception as e:
                print(f"Listener error for {device.path}: {e}")
        
        # Start listeners
        threads = []
        for device in keyboards:
            thread = threading.Thread(target=listen_device, args=(device,), daemon=True)
            thread.start()
            threads.append(thread)
        
        # Monitor output
        line_buffers = {}
        print("\n📊 LIVE SENSOR DATA:")
        print("-" * 40)
        
        while self.running:
            try:
                device_path, char = data_queue.get(timeout=1.0)
                
                if device_path not in line_buffers:
                    line_buffers[device_path] = ""
                
                if char == '\n':
                    if line_buffers[device_path]:
                        line = line_buffers[device_path]
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"\n[{timestamp}] {line}")
                        
                        # Parse the line
                        import re
                        match = re.match(r"(\d+\.\d+)\s*\[C\]\s*(\d+\.\d+)\s*\[%RH\]\s*(\d+)S", line)
                        if match:
                            temp = float(match.group(1))
                            humidity = float(match.group(2))
                            interval = int(match.group(3))
                            print(f"    📊 SENSOR: {temp}°C, {humidity}% RH, {interval}s interval")
                        elif "TEMPERHUM" in line.upper() or "PCSENSOR" in line.upper():
                            print(f"    🏷️  BANNER: {line}")
                        else:
                            print(f"    ❓ UNKNOWN: {line}")
                        
                        line_buffers[device_path] = ""
                else:
                    line_buffers[device_path] += char
                    print(char, end='', flush=True)
                    
            except Empty:
                continue
            except KeyboardInterrupt:
                break

def main():
    test = ManualTest()
    test.monitor_manual_activation()

if __name__ == "__main__":
    main()