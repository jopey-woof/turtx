#!/usr/bin/env python3
"""
Direct HID Raw Control Test for TemperhUM Sensors
"""
import os
import time
import struct

class HidRawControlTest:
    def __init__(self):
        self.temperhum_hidraw_devices = []
        
    def find_temperhum_hidraw_devices(self):
        """Find TemperhUM hidraw devices"""
        devices = []
        for i in range(20):  # Check hidraw0 through hidraw19
            hidraw_path = f'/dev/hidraw{i}'
            if os.path.exists(hidraw_path):
                try:
                    link = os.readlink(f'/sys/class/hidraw/hidraw{i}')
                    if '3553' in link:
                        # Determine which USB device and interface
                        if '1-1:1.0' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-1', 'interface': 0, 'desc': 'Sensor1-Interface0'}
                        elif '1-1:1.1' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-1', 'interface': 1, 'desc': 'Sensor1-Interface1'}
                        elif '1-2:1.0' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-2', 'interface': 0, 'desc': 'Sensor2-Interface0'}
                        elif '1-2:1.1' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-2', 'interface': 1, 'desc': 'Sensor2-Interface1'}
                        else:
                            device_info = {'path': hidraw_path, 'usb': 'unknown', 'interface': -1, 'desc': f'Unknown-{hidraw_path}'}
                        
                        devices.append(device_info)
                except:
                    pass
        
        return devices
    
    def send_hidraw_command(self, device_path, command_name, command_bytes):
        """Send command via hidraw device"""
        print(f"    Sending {command_name} to {device_path}")
        print(f"    Command: {[hex(b) for b in command_bytes]}")
        
        try:
            with open(device_path, 'r+b') as f:
                # Write the command
                bytes_written = f.write(bytes(command_bytes))
                f.flush()
                
                print(f"    ✅ Wrote {bytes_written} bytes")
                return True
                
        except PermissionError:
            print(f"    ❌ Permission denied - run with sudo")
            return False
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return False
    
    def test_keyboard_commands_on_device(self, device_info):
        """Test keyboard commands on a specific hidraw device"""
        device_path = device_info['path']
        desc = device_info['desc']
        
        print(f"\n🎯 Testing {desc} ({device_path}):")
        
        # Standard HID keyboard report format: [modifier, reserved, key1, key2, key3, key4, key5, key6]
        commands = {
            "Caps Lock Press": [0x00, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Caps Lock Release": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Num Lock Press": [0x00, 0x00, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Num Lock Release": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        }
        
        success = False
        
        # Test 1: Caps Lock Hold (toggle output)
        print(f"  TEST 1: Caps Lock Hold (1 second)")
        if self.send_hidraw_command(device_path, "Caps Lock Press", commands["Caps Lock Press"]):
            time.sleep(1.0)
            self.send_hidraw_command(device_path, "Caps Lock Release", commands["Caps Lock Release"])
            success = True
        
        time.sleep(0.5)
        
        # Test 2: Caps Lock Double Press (increase interval)
        print(f"  TEST 2: Caps Lock Double Press")
        if self.send_hidraw_command(device_path, "Caps Lock Press", commands["Caps Lock Press"]):
            self.send_hidraw_command(device_path, "Caps Lock Release", commands["Caps Lock Release"])
            time.sleep(0.1)
            self.send_hidraw_command(device_path, "Caps Lock Press", commands["Caps Lock Press"])
            self.send_hidraw_command(device_path, "Caps Lock Release", commands["Caps Lock Release"])
            success = True
        
        time.sleep(0.5)
        
        # Test 3: Num Lock Double Press (decrease interval)
        print(f"  TEST 3: Num Lock Double Press")
        if self.send_hidraw_command(device_path, "Num Lock Press", commands["Num Lock Press"]):
            self.send_hidraw_command(device_path, "Num Lock Release", commands["Num Lock Release"])
            time.sleep(0.1)
            self.send_hidraw_command(device_path, "Num Lock Press", commands["Num Lock Press"])
            self.send_hidraw_command(device_path, "Num Lock Release", commands["Num Lock Release"])
            success = True
        
        return success
    
    def run_hidraw_test(self):
        """Run the hidraw control test"""
        print("🔧 HIDRAW CONTROL TEST")
        print("=" * 30)
        print("Testing direct hidraw access for sensor control")
        print()
        
        # Find TemperhUM hidraw devices
        devices = self.find_temperhum_hidraw_devices()
        
        if not devices:
            print("❌ No TemperhUM hidraw devices found!")
            return False
        
        print(f"📡 Found {len(devices)} TemperhUM hidraw devices:")
        for device in devices:
            print(f"  {device['desc']}: {device['path']}")
        
        # Test each device
        any_success = False
        for device in devices:
            success = self.test_keyboard_commands_on_device(device)
            if success:
                any_success = True
                
                # Give time for changes to take effect
                print(f"  ⏳ Waiting 3 seconds for changes...")
                time.sleep(3)
        
        if any_success:
            print(f"\n✅ Commands sent successfully!")
            print(f"Now run the live monitor to see if anything changed:")
            print(f"python3 live_sensor_monitor.py")
        else:
            print(f"\n❌ All commands failed")
            print(f"Try running with sudo:")
            print(f"sudo python3 hidraw_control_test.py")
        
        return any_success

def main():
    test = HidRawControlTest()
    test.run_hidraw_test()

if __name__ == "__main__":
    main()