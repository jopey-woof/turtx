#!/usr/bin/env python3
"""
Systematic Control Test - Try various HID command formats to find working control protocol
"""
import os
import time
import evdev

class SystematicControlTest:
    def __init__(self):
        self.test_results = []
        
    def find_temperhum_hidraw_devices(self):
        """Find TemperhUM hidraw devices"""
        devices = []
        for i in range(20):
            hidraw_path = f'/dev/hidraw{i}'
            if os.path.exists(hidraw_path):
                try:
                    link = os.readlink(f'/sys/class/hidraw/hidraw{i}')
                    if '3553' in link:
                        if '1-1:1.1' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-1', 'interface': 1, 'desc': 'Sensor1-Control'}
                        elif '1-2:1.1' in link:
                            device_info = {'path': hidraw_path, 'usb': '1-2', 'interface': 1, 'desc': 'Sensor2-Control'}
                        else:
                            continue  # Skip Interface 0 (data output)
                        
                        devices.append(device_info)
                except:
                    pass
        
        return devices
    
    def get_current_sensor_state(self):
        """Get current state of sensors for comparison"""
        try:
            evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            temperhum_count = len([d for d in evdev_devices if "TEMPerHUM" in d.name])
            return {'keyboard_interfaces': temperhum_count}
        except:
            return {'keyboard_interfaces': 0}
    
    def send_command_sequence(self, device_path, sequence_name, commands):
        """Send a sequence of HID commands"""
        print(f"    Testing {sequence_name}...")
        
        try:
            with open(device_path, 'r+b') as f:
                for i, (cmd_name, cmd_bytes, delay) in enumerate(commands):
                    f.write(bytes(cmd_bytes))
                    f.flush()
                    
                    if delay > 0:
                        time.sleep(delay)
                    
                    # Brief delay between commands
                    time.sleep(0.05)
                
                print(f"      ✅ Sent {len(commands)} commands")
                return True
                
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            return False
    
    def test_control_sequences(self, device_info):
        """Test various control command sequences"""
        device_path = device_info['path']
        desc = device_info['desc']
        
        print(f"\n🎯 Testing {desc} ({device_path}):")
        
        # Get initial state
        initial_state = self.get_current_sensor_state()
        
        # Test sequences based on different HID report formats
        test_sequences = {
            "Standard Keyboard - Caps Lock Hold": [
                ("Caps Press", [0x00, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00], 0),
                ("Hold", [], 1.0),
                ("Caps Release", [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0)
            ],
            
            "Boot Protocol - Caps Lock Hold": [
                ("Caps Press", [0x00, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00], 0),
                ("Hold", [], 1.0),
                ("Caps Release", [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0)
            ],
            
            "Raw HID Report - Caps Lock": [
                ("Raw Caps", [0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 1.0),
                ("Raw Release", [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0)
            ],
            
            "Feature Report - Control": [
                ("Feature", [0x01, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 1.0),
                ("Clear", [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0)
            ],
            
            "Vendor Specific - Toggle": [
                ("Vendor Cmd", [0xFF, 0x01, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00], 1.0),
                ("Vendor Clear", [0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0)
            ],
            
            "Mouse Report - Button Hold": [
                ("Mouse Press", [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 1.0),
                ("Mouse Release", [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0)
            ],
            
            "Double Click Simulation": [
                ("Click 1", [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0),
                ("Release 1", [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0.1),
                ("Click 2", [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0),
                ("Release 2", [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0)
            ],
            
            "Consumer Control - Media Key": [
                ("Media Key", [0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00], 1.0),
                ("Media Clear", [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], 0)
            ]
        }
        
        successful_sequences = []
        
        for seq_name, commands in test_sequences.items():
            # Send the command sequence
            success = self.send_command_sequence(device_path, seq_name, commands)
            
            if success:
                # Wait for potential effects
                time.sleep(2)
                
                # Check for changes
                new_state = self.get_current_sensor_state()
                
                if new_state != initial_state:
                    print(f"      🎉 STATE CHANGE DETECTED!")
                    print(f"         Before: {initial_state}")
                    print(f"         After: {new_state}")
                    successful_sequences.append(seq_name)
                    
                    # Update initial state for next test
                    initial_state = new_state
                else:
                    print(f"      ⚪ No visible changes")
            
            # Brief pause between test sequences
            time.sleep(0.5)
        
        return successful_sequences
    
    def run_systematic_test(self):
        """Run systematic control testing"""
        print("🧪 SYSTEMATIC CONTROL TEST")
        print("=" * 35)
        print("Testing various HID command formats to find working control protocol")
        print()
        
        if os.geteuid() != 0:
            print("❌ Need sudo access for hidraw devices")
            print("Run with: sudo python3 systematic_control_test.py")
            return False
        
        # Find control interfaces (Interface 1 only)
        devices = self.find_temperhum_hidraw_devices()
        
        if not devices:
            print("❌ No TemperhUM control interfaces found!")
            return False
        
        print(f"📡 Found {len(devices)} control interfaces:")
        for device in devices:
            print(f"  {device['desc']}: {device['path']}")
        
        print(f"\n🔬 TESTING PHASE:")
        print("Each test will:")
        print("1. Send HID command sequence")
        print("2. Wait for effects (2 seconds)")
        print("3. Check for changes in sensor state")
        print()
        
        all_successful = []
        
        # Test each device
        for device in devices:
            successful = self.test_control_sequences(device)
            if successful:
                all_successful.extend([(device['desc'], seq) for seq in successful])
        
        # Summary
        print(f"\n📋 TEST RESULTS SUMMARY:")
        print("-" * 30)
        
        if all_successful:
            print(f"✅ Found {len(all_successful)} working command sequences:")
            for device, sequence in all_successful:
                print(f"  • {device}: {sequence}")
            
            print(f"\n🚀 NEXT STEPS:")
            print("1. Use the working sequences for programmatic control")
            print("2. Test interval adjustment commands")
            print("3. Build the final automation system")
            
        else:
            print("❌ No working command sequences found")
            print("\nPossible reasons:")
            print("1. Commands work but changes aren't immediately visible")
            print("2. Need different timing or command format")
            print("3. Sensors might require specific initialization sequence")
            print("4. Control might require physical button press first")
        
        return len(all_successful) > 0

def main():
    test = SystematicControlTest()
    test.run_systematic_test()

if __name__ == "__main__":
    main()