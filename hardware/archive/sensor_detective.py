[%rh] 1s
29.28 [c] 41.24 [%rh] 1s
29.32 [c] 41.40 [%rh] 1s
29.35 [c] 41.32 [%rh] 1s
29.29 [c] 40.99 [%rh] 1s
#!/usr/bin/env python3
"""
TemperhUM Sensor Detective - Comprehensive sensor detection and interface analysis
"""
import hid
import evdev
import os
import sys
import time
import threading
from queue import Queue, Empty
import re

class SensorDetective:
    def __init__(self):
        self.vendor_id = 0x3553
        self.product_id = 0xa001
        self.sensors = []
        
    def detect_sensors(self):
        """Detect all TemperhUM sensors and their interfaces"""
        print("🔍 DETECTING TEMPERHUM SENSORS...")
        print("=" * 50)
        
        # HID Interface Detection
        hid_devices = hid.enumerate(self.vendor_id, self.product_id)
        print(f"Found {len(hid_devices)} HID interfaces:")
        
        sensor_groups = {}
        for device in hid_devices:
            path = device['path'].decode()
            interface_num = device['interface_number']
            usage = device.get('usage', 'Unknown')
            usage_page = device.get('usage_page', 'Unknown')
            
            # Extract base USB path (before interface number)
            base_path = path.split(':')[0]  # e.g., "0001:0002" from "0001:0002:00"
            
            if base_path not in sensor_groups:
                sensor_groups[base_path] = {}
            
            sensor_groups[base_path][interface_num] = {
                'path': path,
                'usage': usage,
                'usage_page': usage_page,
                'interface_number': interface_num
            }
            
            print(f"  Interface {interface_num}: {path}")
            print(f"    Usage: {usage} (Page: {usage_page})")
            
        print(f"\nGrouped into {len(sensor_groups)} physical sensors:")
        for i, (base_path, interfaces) in enumerate(sensor_groups.items(), 1):
            print(f"  Sensor {i} ({base_path}): {len(interfaces)} interfaces")
            for int_num, int_data in interfaces.items():
                print(f"    Interface {int_num}: Usage {int_data['usage']}")
        
        # EVDEV Detection
        print(f"\n🎹 EVDEV KEYBOARD INTERFACES:")
        evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        temperhum_keyboards = [d for d in evdev_devices if "TEMPerHUM" in d.name]
        
        print(f"Found {len(temperhum_keyboards)} keyboard interfaces:")
        for device in temperhum_keyboards:
            print(f"  {device.path}: {device.name}")
            print(f"    Physical: {device.phys}")
            print(f"    Vendor: 0x{device.info.vendor:04x}, Product: 0x{device.info.product:04x}")
        
        # Store results
        self.hid_interfaces = hid_devices
        self.sensor_groups = sensor_groups
        self.keyboard_interfaces = temperhum_keyboards
        
        return len(sensor_groups)
    
    def test_hid_communication(self):
        """Test HID communication with each interface"""
        print(f"\n🔧 TESTING HID COMMUNICATION...")
        print("=" * 50)
        
        for i, (base_path, interfaces) in enumerate(self.sensor_groups.items(), 1):
            print(f"\nTesting Sensor {i} ({base_path}):")
            
            for interface_num, interface_data in interfaces.items():
                print(f"  Testing Interface {interface_num}...")
                path = interface_data['path'].encode()
                
                try:
                    device = hid.device()
                    device.open_path(path)
                    
                    # Get device info
                    manufacturer = device.get_manufacturer_string()
                    product = device.get_product_string()
                    serial = device.get_serial_number_string()
                    
                    print(f"    ✓ Connected successfully")
                    print(f"    Manufacturer: {manufacturer}")
                    print(f"    Product: {product}")
                    print(f"    Serial: {serial}")
                    
                    # Test sending a command (Caps Lock toggle)
                    caps_lock_command = [0x00, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00]
                    try:
                        result = device.write(caps_lock_command)
                        print(f"    ✓ Command sent successfully (wrote {result} bytes)")
                        
                        # Try to read response (non-blocking)
                        device.set_nonblocking(True)
                        try:
                            response = device.read(8, timeout_ms=100)
                            if response:
                                print(f"    ✓ Response received: {[hex(b) for b in response]}")
                            else:
                                print(f"    ℹ No immediate response (normal for control interface)")
                        except Exception as e:
                            print(f"    ℹ No response read (normal): {e}")
                            
                    except Exception as e:
                        print(f"    ✗ Command failed: {e}")
                    
                    device.close()
                    
                except Exception as e:
                    print(f"    ✗ Connection failed: {e}")
    
    def monitor_keyboard_output(self, duration=10):
        """Monitor keyboard output from all TemperhUM interfaces"""
        print(f"\n⌨️  MONITORING KEYBOARD OUTPUT ({duration}s)...")
        print("=" * 50)
        print("Please manually press Caps Lock on a sensor to activate it...")
        
        if not self.keyboard_interfaces:
            print("No keyboard interfaces found!")
            return
        
        # Keycode to character mapping
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
        
        def listen_device(device, device_name):
            """Listen to a single device"""
            print(f"📡 Listening on {device_name}...")
            try:
                for event in device.read_loop():
                    if event.type == evdev.ecodes.EV_KEY:
                        key_event = evdev.categorize(event)
                        if key_event.keystate == key_event.key_down:
                            char = keycode_map.get(key_event.scancode)
                            if char:
                                data_queue.put((device_name, char))
            except Exception as e:
                print(f"Error listening to {device_name}: {e}")
        
        # Start listener threads
        for device in self.keyboard_interfaces:
            thread = threading.Thread(
                target=listen_device, 
                args=(device, f"{device.path}({device.name})"),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Monitor output
        line_buffers = {}
        start_time = time.time()
        
        print(f"Monitoring for {duration} seconds...")
        print("Raw output will appear below:\n")
        
        while time.time() - start_time < duration:
            try:
                device_name, char = data_queue.get(timeout=0.1)
                
                if device_name not in line_buffers:
                    line_buffers[device_name] = ""
                
                if char == '\n':
                    if line_buffers[device_name]:
                        line = line_buffers[device_name]
                        print(f"[{device_name}] {line}")
                        
                        # Try to parse the line
                        self.parse_sensor_line(line, device_name)
                        
                        line_buffers[device_name] = ""
                else:
                    line_buffers[device_name] += char
                    print(char, end='', flush=True)
                    
            except Empty:
                continue
        
        print(f"\n\nMonitoring completed after {duration} seconds.")
    
    def parse_sensor_line(self, line, source):
        """Parse a sensor data line"""
        # Try to match temperature/humidity pattern
        match = re.match(r"(\d+\.\d+)\s*\[C\]\s*(\d+\.\d+)\s*\[%RH\]\s*(\d+)S", line)
        if match:
            temp = float(match.group(1))
            humidity = float(match.group(2))
            interval = int(match.group(3))
            
            print(f"    📊 PARSED: Temp={temp}°C, Humidity={humidity}%, Interval={interval}s")
            return True
        
        # Check for banner/configuration text
        if any(keyword in line.upper() for keyword in ['TEMPERHUM', 'PCSENSOR', 'CAPS LOCK', 'NUM LOCK']):
            print(f"    🏷️  BANNER: {line}")
            return True
        
        print(f"    ❓ UNKNOWN: {line}")
        return False
    
    def test_programmatic_control(self):
        """Test programmatic control of sensors"""
        print(f"\n🎮 TESTING PROGRAMMATIC CONTROL...")
        print("=" * 50)
        
        if not self.sensor_groups:
            print("No sensors detected!")
            return
        
        # Test control commands on each sensor
        for i, (base_path, interfaces) in enumerate(self.sensor_groups.items(), 1):
            print(f"\nTesting control on Sensor {i} ({base_path}):")
            
            # Look for interface that might accept control commands
            # Usually interface 1 (mouse protocol) for control
            control_interface = None
            for interface_num, interface_data in interfaces.items():
                if interface_num == 1:  # Mouse interface typically for control
                    control_interface = interface_data
                    break
            
            if not control_interface:
                print("  No control interface found (looking for interface 1)")
                continue
            
            path = control_interface['path'].encode()
            print(f"  Using interface {control_interface['interface_number']} for control")
            
            try:
                device = hid.device()
                device.open_path(path)
                
                print("  Sending Caps Lock toggle command...")
                
                # Send Caps Lock press
                caps_press = [0x00, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00]
                device.write(caps_press)
                time.sleep(0.1)
                
                # Send Caps Lock release
                caps_release = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                device.write(caps_release)
                
                print("  ✓ Control commands sent")
                print("  📺 Watch for sensor activation in keyboard monitoring...")
                
                device.close()
                
            except Exception as e:
                print(f"  ✗ Control test failed: {e}")
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 TEMPERHUM SENSOR COMPREHENSIVE TEST")
        print("=" * 60)
        
        # Step 1: Detection
        sensor_count = self.detect_sensors()
        if sensor_count == 0:
            print("❌ No sensors detected!")
            return False
        
        print(f"\n✅ Detected {sensor_count} sensors with dual interfaces each")
        
        # Step 2: HID Communication Test
        self.test_hid_communication()
        
        # Step 3: Programmatic Control Test
        self.test_programmatic_control()
        
        # Step 4: Monitor for results
        print(f"\n⏰ Now monitoring keyboard output for 15 seconds...")
        print("If programmatic control worked, you should see sensor data appear...")
        self.monitor_keyboard_output(15)
        
        return True

def main():
    detective = SensorDetective()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "detect":
            detective.detect_sensors()
        elif command == "monitor":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            detective.detect_sensors()
            detective.monitor_keyboard_output(duration)
        elif command == "control":
            detective.detect_sensors()
            detective.test_programmatic_control()
        elif command == "hid":
            detective.detect_sensors()
            detective.test_hid_communication()
        else:
            print("Usage: python3 sensor_detective.py [detect|monitor|control|hid|comprehensive]")
    else:
        # Run comprehensive test by default
        detective.run_comprehensive_test()

if __name__ == "__main__":
    main()