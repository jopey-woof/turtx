#!/usr/bin/env python3
"""
Correct HID Format Test - Send proper generic HID reports to Interface 1
"""
import os
import time
import evdev

class CorrectHIDFormatTest:
    def __init__(self):
        pass
        
    def find_control_interfaces(self):
        """Find TemperhUM Interface 1 devices (generic HID)"""
        devices = []
        for i in range(20):
            hidraw_path = f'/dev/hidraw{i}'
            if os.path.exists(hidraw_path):
                try:
                    link = os.readlink(f'/sys/class/hidraw/hidraw{i}')
                    if '3553' in link and '1.1' in link:  # Interface 1
                        if '1-1:1.1' in link:
                            desc = 'Sensor1-Control'
                        elif '1-2:1.1' in link:
                            desc = 'Sensor2-Control'
                        else:
                            desc = f'Unknown-{hidraw_path}'
                        
                        devices.append({'path': hidraw_path, 'desc': desc})
                except:
                    pass
        
        return devices
    
    def get_sensor_state(self):
        """Get current sensor state"""
        try:
            evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            temperhum_count = len([d for d in evdev_devices if "TEMPerHUM" in d.name])
            return temperhum_count
        except:
            return 0
    
    def send_generic_hid_command(self, device_path, command_name, data_bytes):
        """Send generic HID command (8 bytes as per report descriptor)"""
        print(f"    {command_name}: {[hex(b) for b in data_bytes]}")
        
        try:
            with open(device_path, 'wb') as f:
                f.write(bytes(data_bytes))
                f.flush()
            return True
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            return False
    
    def test_generic_hid_commands(self, device_info):
        """Test generic HID commands based on report descriptor analysis"""
        device_path = device_info['path']
        desc = device_info['desc']
        
        print(f"\n🎯 Testing {desc} ({device_path}):")
        print("Using generic HID format (not keyboard format)")
        
        initial_state = self.get_sensor_state()
        print(f"Initial sensor interfaces: {initial_state}")
        
        # Based on report descriptor analysis:
        # Interface 1 expects 8-byte generic HID reports
        # Let's try various patterns that might represent control commands
        
        test_commands = {
            "Generic Toggle 1": [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Generic Toggle 2": [0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Caps Lock Equivalent": [0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Caps Lock Hold Pattern": [0x39, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Control Byte Pattern 1": [0xFF, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Control Byte Pattern 2": [0x01, 0x39, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Windows-style Command 1": [0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Windows-style Command 2": [0x00, 0x02, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Raw Caps Lock Code": [0x00, 0x00, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00],
            "Feature Report Style": [0x01, 0x01, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Num Lock Equivalent": [0x53, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Interval Increase": [0x00, 0x39, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00],  # Double Caps
            "Interval Decrease": [0x00, 0x53, 0x53, 0x00, 0x00, 0x00, 0x00, 0x00],  # Double Num
        }
        
        successful_commands = []
        
        for cmd_name, cmd_bytes in test_commands.items():
            print(f"\n  Testing: {cmd_name}")
            
            # Send command
            if self.send_generic_hid_command(device_path, "Send", cmd_bytes):
                # Hold for 1 second for toggle commands
                if "Toggle" in cmd_name or "Hold" in cmd_name or "Caps" in cmd_name:
                    time.sleep(1.0)
                    # Send "release" (all zeros)
                    self.send_generic_hid_command(device_path, "Release", [0x00] * 8)
                
                # Wait for effects
                time.sleep(2.0)
                
                # Check for changes
                new_state = self.get_sensor_state()
                if new_state != initial_state:
                    print(f"      🎉 SUCCESS! State changed: {initial_state} → {new_state}")
                    successful_commands.append(cmd_name)
                    initial_state = new_state  # Update for next test
                else:
                    print(f"      ⚪ No change detected")
            
            # Brief pause between tests
            time.sleep(0.5)
        
        return successful_commands
    
    def run_correct_format_test(self):
        """Run the correct HID format test"""
        print("🔧 CORRECT HID FORMAT TEST")
        print("=" * 30)
        print("Testing generic HID commands on Interface 1 (not keyboard format)")
        print()
        
        if os.geteuid() != 0:
            print("❌ Need sudo for hidraw access")
            print("Run: sudo python3 correct_hid_format_test.py")
            return False
        
        # Find control interfaces
        devices = self.find_control_interfaces()
        
        if not devices:
            print("❌ No control interfaces found!")
            return False
        
        print(f"📡 Found {len(devices)} control interfaces:")
        for device in devices:
            print(f"  {device['desc']}: {device['path']}")
        
        # Test each device
        all_successful = []
        for device in devices:
            successful = self.test_generic_hid_commands(device)
            if successful:
                all_successful.extend([(device['desc'], cmd) for cmd in successful])
        
        # Results
        print(f"\n📋 RESULTS:")
        print("-" * 15)
        
        if all_successful:
            print(f"✅ Found {len(all_successful)} working commands:")
            for device, command in all_successful:
                print(f"  • {device}: {command}")
            
            print(f"\n🚀 SUCCESS! We found the correct HID format!")
            print("Now we can implement programmatic sensor control!")
        else:
            print("❌ No working commands found with generic HID format")
            print("May need to try different approaches or investigate Windows behavior")
        
        return len(all_successful) > 0

def main():
    test = CorrectHIDFormatTest()
    test.run_correct_format_test()

if __name__ == "__main__":
    main()