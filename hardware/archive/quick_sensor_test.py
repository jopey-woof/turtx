#!/usr/bin/env python3
"""
Quick TemperhUM Sensor Test - Fast activation test with timeouts
"""
import hid
import time
import evdev
import threading
import signal
import sys
from queue import Queue, Empty

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

class QuickSensorTest:
    def __init__(self):
        self.vendor_id = 0x3553
        self.product_id = 0xa001
        
    def get_sensors(self):
        """Get sensor interfaces with timeout"""
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)  # 5 second timeout
        
        try:
            hid_devices = hid.enumerate(self.vendor_id, self.product_id)
            sensor_groups = {}
            
            for device in hid_devices:
                path = device['path'].decode()
                interface_num = device['interface_number']
                base_path = path.split(':')[0]
                
                if base_path not in sensor_groups:
                    sensor_groups[base_path] = {}
                
                sensor_groups[base_path][interface_num] = device['path']
            
            signal.alarm(0)  # Cancel timeout
            return sensor_groups
            
        except TimeoutError:
            print("❌ Sensor enumeration timed out")
            return {}
        except Exception as e:
            signal.alarm(0)
            print(f"❌ Error getting sensors: {e}")
            return {}
    
    def check_keyboards_quick(self):
        """Quick keyboard interface check with timeout"""
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(3)  # 3 second timeout
        
        try:
            evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            temperhum_keyboards = [d for d in evdev_devices if "TEMPerHUM" in d.name]
            signal.alarm(0)
            return temperhum_keyboards
        except TimeoutError:
            print("⚠️ Keyboard check timed out")
            return []
        except Exception as e:
            signal.alarm(0)
            print(f"⚠️ Keyboard check error: {e}")
            return []
    
    def try_activate_sensor(self, device_path, sensor_name, timeout=3):
        """Try to activate a sensor with timeout"""
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            device = hid.device()
            device.open_path(device_path)
            
            print(f"  🔧 Activating {sensor_name}...")
            
            # Method 1: Hold Caps Lock for 1 second (most reliable)
            caps_press = [0x00, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00]
            caps_release = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            
            device.write(caps_press)
            time.sleep(1.0)
            device.write(caps_release)
            
            device.close()
            signal.alarm(0)
            print(f"  ✓ Commands sent to {sensor_name}")
            return True
            
        except TimeoutError:
            print(f"  ⚠️ Activation timed out for {sensor_name}")
            return False
        except Exception as e:
            signal.alarm(0)
            print(f"  ❌ Activation failed for {sensor_name}: {e}")
            return False
    
    def monitor_quick(self, keyboards, timeout=5):
        """Quick monitoring with timeout"""
        if not keyboards:
            print("No keyboards to monitor")
            return
        
        print(f"📡 Monitoring {len(keyboards)} keyboard(s) for {timeout} seconds...")
        
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
                device.grab()  # Exclusive access
                for event in device.read_loop():
                    if event.type == evdev.ecodes.EV_KEY:
                        key_event = evdev.categorize(event)
                        if key_event.keystate == key_event.key_down:
                            char = keycode_map.get(key_event.scancode)
                            if char:
                                data_queue.put((device.path, char))
            except Exception as e:
                print(f"Listener error for {device.path}: {e}")
        
        # Start listeners with timeout
        threads = []
        for device in keyboards:
            thread = threading.Thread(target=listen_device, args=(device,), daemon=True)
            thread.start()
            threads.append(thread)
            print(f"  📡 Listening on {device.path}")
        
        # Monitor with timeout
        line_buffers = {}
        start_time = time.time()
        data_received = False
        
        while time.time() - start_time < timeout:
            try:
                device_path, char = data_queue.get(timeout=0.5)
                data_received = True
                
                if device_path not in line_buffers:
                    line_buffers[device_path] = ""
                
                if char == '\n':
                    if line_buffers[device_path]:
                        line = line_buffers[device_path]
                        print(f"📊 [{device_path}] {line}")
                        
                        # Quick parse
                        import re
                        match = re.match(r"(\d+\.\d+)\s*\[C\]\s*(\d+\.\d+)\s*\[%RH\]\s*(\d+)S", line)
                        if match:
                            temp, humidity, interval = match.groups()
                            print(f"    ✅ PARSED: {temp}°C, {humidity}% RH, {interval}s")
                        
                        line_buffers[device_path] = ""
                else:
                    line_buffers[device_path] += char
                    print(char, end='', flush=True)
                    
            except Empty:
                continue
        
        # Clean up
        for device in keyboards:
            try:
                device.ungrab()
            except:
                pass
        
        if data_received:
            print(f"\n✅ Data received successfully!")
        else:
            print(f"\n⚠️ No data received in {timeout} seconds")
    
    def run_quick_test(self):
        """Run quick sensor test with timeouts"""
        print("🚀 QUICK TEMPERHUM SENSOR TEST")
        print("=" * 40)
        
        # Step 1: Get sensors (5s timeout)
        print("1️⃣ Detecting sensors...")
        sensors = self.get_sensors()
        if not sensors:
            print("❌ No sensors found!")
            return False
        
        print(f"✅ Found {len(sensors)} sensors")
        
        # Step 2: Check initial keyboards (3s timeout)
        print("\n2️⃣ Checking initial keyboard interfaces...")
        initial_keyboards = self.check_keyboards_quick()
        print(f"📋 Initial keyboards: {len(initial_keyboards)}")
        
        # Step 3: Try activation (3s timeout per sensor)
        print("\n3️⃣ Attempting sensor activation...")
        activation_success = False
        
        for i, (base_path, interfaces) in enumerate(sensors.items(), 1):
            print(f"Sensor {i} ({base_path}):")
            
            # Try interface 1 first (usually control interface)
            if 1 in interfaces:
                success = self.try_activate_sensor(
                    interfaces[1], 
                    f"Sensor-{i}-Interface-1", 
                    timeout=3
                )
                if success:
                    activation_success = True
                    
                # Quick check for new keyboards after each activation
                time.sleep(0.5)  # Brief wait for interface to appear
                new_keyboards = self.check_keyboards_quick()
                if len(new_keyboards) > len(initial_keyboards):
                    print(f"  🎉 New keyboard interface detected!")
                    break
        
        # Step 4: Check final keyboards and monitor (3s timeout)
        print("\n4️⃣ Final keyboard check and monitoring...")
        final_keyboards = self.check_keyboards_quick()
        print(f"📋 Final keyboards: {len(final_keyboards)}")
        
        if final_keyboards:
            self.monitor_quick(final_keyboards, timeout=5)
        else:
            print("❌ No keyboard interfaces found - sensors may not be activated")
        
        return len(final_keyboards) > 0

def main():
    # Set up signal handling for clean exits
    def signal_handler(sig, frame):
        print("\n🛑 Test interrupted")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    test = QuickSensorTest()
    success = test.run_quick_test()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed - sensors not responding")

if __name__ == "__main__":
    main()