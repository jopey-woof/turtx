#!/usr/bin/env python3
"""
TemperhUM Sensor Activator - Advanced sensor activation and control
"""
import hid
import time
import evdev
import threading
from queue import Queue, Empty

class SensorActivator:
    def __init__(self):
        self.vendor_id = 0x3553
        self.product_id = 0xa001
        
    def get_sensors(self):
        """Get all sensor HID interfaces grouped by physical device"""
        hid_devices = hid.enumerate(self.vendor_id, self.product_id)
        sensor_groups = {}
        
        for device in hid_devices:
            path = device['path'].decode()
            interface_num = device['interface_number']
            base_path = path.split(':')[0]
            
            if base_path not in sensor_groups:
                sensor_groups[base_path] = {}
            
            sensor_groups[base_path][interface_num] = device['path']
        
        return sensor_groups
    
    def try_multiple_activation_methods(self, device_path, sensor_name):
        """Try multiple methods to activate a sensor"""
        print(f"🔧 Trying activation methods on {sensor_name}...")
        
        try:
            device = hid.device()
            device.open_path(device_path)
            
            # Method 1: Standard Caps Lock toggle (press and release)
            print("  Method 1: Standard Caps Lock toggle...")
            caps_press = [0x00, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00]
            caps_release = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            
            device.write(caps_press)
            time.sleep(0.1)
            device.write(caps_release)
            time.sleep(0.5)
            
            # Method 2: Hold Caps Lock for 1 second
            print("  Method 2: Hold Caps Lock for 1 second...")
            device.write(caps_press)
            time.sleep(1.0)
            device.write(caps_release)
            time.sleep(0.5)
            
            # Method 3: Different HID report format
            print("  Method 3: Alternative HID report format...")
            alt_press = [0x02, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            alt_release = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            
            device.write(alt_press)
            time.sleep(1.0)
            device.write(alt_release)
            time.sleep(0.5)
            
            # Method 4: Raw Caps Lock scancode
            print("  Method 4: Raw scancode approach...")
            raw_caps = [0x00, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00]
            raw_release = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            
            device.write(raw_caps)
            time.sleep(1.0)
            device.write(raw_release)
            time.sleep(0.5)
            
            # Method 5: Try different modifier combinations
            print("  Method 5: Different modifier combinations...")
            for modifier in [0x01, 0x02, 0x04, 0x08]:  # Different shift states
                mod_cmd = [0x00, modifier, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00]
                device.write(mod_cmd)
                time.sleep(0.5)
                device.write(caps_release)
                time.sleep(0.5)
            
            device.close()
            print(f"  ✓ All activation methods attempted on {sensor_name}")
            
        except Exception as e:
            print(f"  ✗ Activation failed on {sensor_name}: {e}")
    
    def check_for_keyboard_interfaces(self):
        """Check for newly appeared keyboard interfaces"""
        evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        temperhum_keyboards = [d for d in evdev_devices if "TEMPerHUM" in d.name]
        
        print(f"📋 Current keyboard interfaces: {len(temperhum_keyboards)}")
        for device in temperhum_keyboards:
            print(f"  {device.path}: {device.name} (Physical: {device.phys})")
        
        return temperhum_keyboards
    
    def monitor_activation_attempts(self, duration=30):
        """Monitor for sensor activation over time"""
        print(f"🚀 COMPREHENSIVE SENSOR ACTIVATION ATTEMPT")
        print("=" * 60)
        
        sensors = self.get_sensors()
        if not sensors:
            print("❌ No sensors detected!")
            return
        
        print(f"Detected {len(sensors)} physical sensors")
        
        # Initial keyboard interface check
        print("\n📋 Initial keyboard interface check:")
        initial_keyboards = self.check_for_keyboard_interfaces()
        
        # Try activation on all sensor interfaces
        print(f"\n🔧 ACTIVATION PHASE:")
        for i, (base_path, interfaces) in enumerate(sensors.items(), 1):
            print(f"\nActivating Sensor {i} ({base_path}):")
            
            # Try both interfaces for activation
            for interface_num, device_path in interfaces.items():
                sensor_name = f"Sensor-{i}-Interface-{interface_num}"
                self.try_multiple_activation_methods(device_path, sensor_name)
                
                # Check for new keyboard interfaces after each attempt
                new_keyboards = self.check_for_keyboard_interfaces()
                if len(new_keyboards) > len(initial_keyboards):
                    print(f"  🎉 NEW KEYBOARD INTERFACE DETECTED!")
                    for kbd in new_keyboards:
                        if kbd not in initial_keyboards:
                            print(f"    NEW: {kbd.path} - {kbd.name}")
        
        # Final monitoring phase
        print(f"\n👀 MONITORING PHASE ({duration}s):")
        final_keyboards = self.check_for_keyboard_interfaces()
        
        if final_keyboards:
            print("Monitoring keyboard output...")
            self.monitor_keyboard_data(final_keyboards, duration)
        else:
            print("No keyboard interfaces found. Waiting and checking periodically...")
            for i in range(duration):
                time.sleep(1)
                keyboards = self.check_for_keyboard_interfaces()
                if keyboards:
                    print(f"🎉 Keyboard interface appeared after {i+1} seconds!")
                    remaining_time = duration - (i + 1)
                    if remaining_time > 0:
                        self.monitor_keyboard_data(keyboards, remaining_time)
                    break
                if i % 5 == 4:  # Every 5 seconds
                    print(f"  Still waiting... ({i+1}/{duration}s)")
    
    def monitor_keyboard_data(self, keyboards, duration):
        """Monitor keyboard data from active interfaces"""
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
        threads = []
        
        def listen_device(device):
            try:
                for event in device.read_loop():
                    if event.type == evdev.ecodes.EV_KEY:
                        key_event = evdev.categorize(event)
                        if key_event.keystate == key_event.key_down:
                            char = keycode_map.get(key_event.scancode)
                            if char:
                                data_queue.put((device.path, char))
            except Exception as e:
                print(f"Error listening to {device.path}: {e}")
        
        # Start listeners
        for device in keyboards:
            thread = threading.Thread(target=listen_device, args=(device,), daemon=True)
            thread.start()
            threads.append(thread)
            print(f"📡 Started listener for {device.path}")
        
        # Monitor output
        line_buffers = {}
        start_time = time.time()
        
        print(f"\n📊 LIVE SENSOR DATA:")
        print("-" * 40)
        
        while time.time() - start_time < duration:
            try:
                device_path, char = data_queue.get(timeout=0.1)
                
                if device_path not in line_buffers:
                    line_buffers[device_path] = ""
                
                if char == '\n':
                    if line_buffers[device_path]:
                        line = line_buffers[device_path]
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"[{timestamp}] [{device_path}] {line}")
                        
                        # Parse the line
                        import re
                        match = re.match(r"(\d+\.\d+)\s*\[C\]\s*(\d+\.\d+)\s*\[%RH\]\s*(\d+)S", line)
                        if match:
                            temp = float(match.group(1))
                            humidity = float(match.group(2))
                            interval = int(match.group(3))
                            print(f"    📊 SENSOR DATA: {temp}°C, {humidity}% RH, {interval}s interval")
                        
                        line_buffers[device_path] = ""
                else:
                    line_buffers[device_path] += char
                    
            except Empty:
                continue
        
        print(f"\n✅ Monitoring completed after {duration} seconds")

def main():
    activator = SensorActivator()
    activator.monitor_activation_attempts(30)

if __name__ == "__main__":
    main()