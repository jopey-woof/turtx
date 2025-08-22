#!/usr/bin/env python3
"""
Methodical Mouse Control Test for TemperhUM Sensors
Testing the theory that Interface 1 uses mouse commands for control
"""
import hid
import time
import evdev
import threading
from queue import Queue, Empty

class MouseControlTest:
    def __init__(self):
        self.vendor_id = 0x3553
        self.product_id = 0xa001
        
    def find_sensors(self):
        """Find sensor HID interfaces grouped by physical device"""
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
    
    def find_keyboard_interfaces(self):
        """Find active TemperhUM keyboard interfaces"""
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            temperhum_devices = [d for d in devices if "TEMPerHUM" in d.name]
            return temperhum_devices
        except Exception as e:
            print(f"Error finding keyboards: {e}")
            return []
    
    def send_mouse_command(self, device_path, command_name, command_data):
        """Send a mouse command to a sensor interface"""
        print(f"    Sending {command_name}: {[hex(b) for b in command_data]}")
        
        try:
            device = hid.device()
            device.open_path(device_path)
            
            result = device.write(command_data)
            print(f"    Result: {result} bytes written")
            
            device.close()
            return True
            
        except Exception as e:
            print(f"    ERROR: {e}")
            return False
    
    def test_mouse_commands_on_interface(self, sensor_name, interface_path):
        """Test various mouse command patterns on an interface"""
        print(f"\n🖱️  Testing mouse commands on {sensor_name}:")
        
        # Mouse command patterns to try
        commands = {
            "Left Click Press": [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Left Click Release": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Right Click Press": [0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Right Click Release": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Middle Click Press": [0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Middle Click Release": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        }
        
        # Test 1: Left Click & Hold (simulate Caps Lock hold)
        print(f"  TEST 1: Left Click & Hold (1 second)")
        self.send_mouse_command(interface_path, "Left Click Press", commands["Left Click Press"])
        time.sleep(1.0)
        self.send_mouse_command(interface_path, "Left Click Release", commands["Left Click Release"])
        time.sleep(0.5)
        
        # Test 2: Left Double Click (simulate Caps Lock double-press)
        print(f"  TEST 2: Left Double Click")
        self.send_mouse_command(interface_path, "Left Click Press", commands["Left Click Press"])
        self.send_mouse_command(interface_path, "Left Click Release", commands["Left Click Release"])
        time.sleep(0.1)
        self.send_mouse_command(interface_path, "Left Click Press", commands["Left Click Press"])
        self.send_mouse_command(interface_path, "Left Click Release", commands["Left Click Release"])
        time.sleep(0.5)
        
        # Test 3: Right Double Click (simulate Num Lock double-press)
        print(f"  TEST 3: Right Double Click")
        self.send_mouse_command(interface_path, "Right Click Press", commands["Right Click Press"])
        self.send_mouse_command(interface_path, "Right Click Release", commands["Right Click Release"])
        time.sleep(0.1)
        self.send_mouse_command(interface_path, "Right Click Press", commands["Right Click Press"])
        self.send_mouse_command(interface_path, "Right Click Release", commands["Right Click Release"])
        time.sleep(0.5)
        
        print(f"  Mouse command tests completed for {sensor_name}")
    
    def monitor_for_changes(self, duration=5):
        """Monitor for keyboard interface changes or data output"""
        print(f"\n👀 Monitoring for changes ({duration}s)...")
        
        initial_keyboards = self.find_keyboard_interfaces()
        print(f"Initial keyboards: {len(initial_keyboards)}")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            current_keyboards = self.find_keyboard_interfaces()
            if len(current_keyboards) != len(initial_keyboards):
                print(f"🎉 CHANGE DETECTED! Keyboards: {len(initial_keyboards)} → {len(current_keyboards)}")
                return True
            time.sleep(0.5)
        
        print("No changes detected")
        return False
    
    def run_methodical_test(self):
        """Run methodical mouse control test"""
        print("🖱️  METHODICAL MOUSE CONTROL TEST")
        print("=" * 45)
        print("Testing theory: Interface 1 = Mouse control")
        print()
        
        # Step 1: Find sensors
        sensors = self.find_sensors()
        if not sensors:
            print("❌ No sensors found!")
            return False
        
        print(f"📡 Found {len(sensors)} physical sensors:")
        for i, (base_path, interfaces) in enumerate(sensors.items(), 1):
            print(f"  Sensor {i} ({base_path}): Interfaces {list(interfaces.keys())}")
        
        # Step 2: Check initial state
        print(f"\n📋 Initial keyboard interfaces:")
        initial_keyboards = self.find_keyboard_interfaces()
        for kbd in initial_keyboards:
            print(f"  {kbd.path}: {kbd.phys}")
        
        # Step 3: Test each sensor's Interface 1 (mouse interface)
        for i, (base_path, interfaces) in enumerate(sensors.items(), 1):
            sensor_name = f"Sensor-{i}"
            
            if 1 in interfaces:  # Interface 1 = Mouse
                print(f"\n🎯 TESTING {sensor_name} Interface 1 (Mouse)")
                print("-" * 40)
                
                interface_path = interfaces[1]
                self.test_mouse_commands_on_interface(sensor_name, interface_path)
                
                # Monitor for changes after each sensor test
                changes_detected = self.monitor_for_changes(5)
                
                if changes_detected:
                    print(f"✅ {sensor_name} responded to mouse commands!")
                    break
                else:
                    print(f"⚠️ No response from {sensor_name}")
            else:
                print(f"❌ {sensor_name} has no Interface 1")
        
        # Step 4: Final state check
        print(f"\n📋 Final keyboard interfaces:")
        final_keyboards = self.find_keyboard_interfaces()
        for kbd in final_keyboards:
            print(f"  {kbd.path}: {kbd.phys}")
        
        success = len(final_keyboards) > len(initial_keyboards)
        
        if success:
            print(f"\n🎉 SUCCESS! Mouse control theory confirmed!")
            print(f"Keyboards: {len(initial_keyboards)} → {len(final_keyboards)}")
        else:
            print(f"\n❌ Mouse control theory not confirmed")
            print("May need to try different command patterns")
        
        return success

def main():
    test = MouseControlTest()
    test.run_methodical_test()

if __name__ == "__main__":
    main()