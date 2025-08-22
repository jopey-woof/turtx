#!/usr/bin/env python3
"""
Interface Separation Test - Send control commands to non-output interface
"""
import hid
import time
import evdev
import threading
from queue import Queue, Empty

class InterfaceSeparationTest:
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
    
    def find_active_keyboard_interfaces(self):
        """Find which evdev interfaces are currently active (outputting data)"""
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            temperhum_devices = [d for d in devices if "TEMPerHUM" in d.name]
            
            active_interfaces = {}
            for device in temperhum_devices:
                # Extract USB path to match with HID interfaces
                # e.g., "usb-0000:03:00.3-2/input0" -> "1-2" and interface 0
                phys = device.phys
                if 'input' in phys:
                    # Parse the physical path to determine USB device and interface
                    if '3-1' in phys:
                        usb_path = '1-1'  # Maps to HID device 1-1
                    elif '3-2' in phys:
                        usb_path = '1-2'  # Maps to HID device 1-2
                    else:
                        continue
                    
                    if 'input0' in phys:
                        interface_num = 0
                    elif 'input1' in phys:
                        interface_num = 1
                    else:
                        continue
                    
                    if usb_path not in active_interfaces:
                        active_interfaces[usb_path] = []
                    active_interfaces[usb_path].append(interface_num)
            
            return active_interfaces
        except Exception as e:
            print(f"Error finding active interfaces: {e}")
            return {}
    
    def send_keyboard_command(self, device_path, command_name, command_data):
        """Send a keyboard command to a HID interface"""
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
    
    def test_control_on_inactive_interface(self, sensor_name, usb_path, interfaces, active_interfaces):
        """Test sending control commands to the interface NOT being used for output"""
        print(f"\n🎯 Testing control on {sensor_name} ({usb_path}):")
        
        # Determine which interface is active (outputting data)
        active_nums = active_interfaces.get(usb_path, [])
        print(f"  Active interfaces (outputting data): {active_nums}")
        
        # Find the inactive interface for control
        all_interfaces = list(interfaces.keys())
        inactive_interfaces = [i for i in all_interfaces if i not in active_nums]
        
        print(f"  Available interfaces: {all_interfaces}")
        print(f"  Inactive interfaces (for control): {inactive_interfaces}")
        
        if not inactive_interfaces:
            print(f"  ⚠️ No inactive interfaces found - trying all interfaces")
            test_interfaces = all_interfaces
        else:
            test_interfaces = inactive_interfaces
        
        # Keyboard commands for Caps Lock and Num Lock
        commands = {
            "Caps Lock Press": [0x00, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00],
            "Caps Lock Release": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            "Num Lock Press": [0x00, 0x00, 0x00, 0x53, 0x00, 0x00, 0x00, 0x00],
            "Num Lock Release": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        }
        
        success = False
        
        for interface_num in test_interfaces:
            interface_path = interfaces[interface_num]
            print(f"\n  Testing Interface {interface_num}:")
            
            # Test 1: Caps Lock Hold (toggle output)
            print(f"    TEST 1: Caps Lock Hold (1 second)")
            if self.send_keyboard_command(interface_path, "Caps Lock Press", commands["Caps Lock Press"]):
                time.sleep(1.0)
                self.send_keyboard_command(interface_path, "Caps Lock Release", commands["Caps Lock Release"])
                success = True
            
            time.sleep(0.5)
            
            # Test 2: Caps Lock Double Press (increase interval)
            print(f"    TEST 2: Caps Lock Double Press")
            if self.send_keyboard_command(interface_path, "Caps Lock Press", commands["Caps Lock Press"]):
                self.send_keyboard_command(interface_path, "Caps Lock Release", commands["Caps Lock Release"])
                time.sleep(0.1)
                self.send_keyboard_command(interface_path, "Caps Lock Press", commands["Caps Lock Press"])
                self.send_keyboard_command(interface_path, "Caps Lock Release", commands["Caps Lock Release"])
                success = True
            
            time.sleep(0.5)
            
            # Test 3: Num Lock Double Press (decrease interval)
            print(f"    TEST 3: Num Lock Double Press")
            if self.send_keyboard_command(interface_path, "Num Lock Press", commands["Num Lock Press"]):
                self.send_keyboard_command(interface_path, "Num Lock Release", commands["Num Lock Release"])
                time.sleep(0.1)
                self.send_keyboard_command(interface_path, "Num Lock Press", commands["Num Lock Press"])
                self.send_keyboard_command(interface_path, "Num Lock Release", commands["Num Lock Release"])
                success = True
            
            time.sleep(1.0)
        
        return success
    
    def monitor_for_changes(self, duration=8):
        """Monitor for changes in keyboard interfaces or data patterns"""
        print(f"\n👀 Monitoring for changes ({duration}s)...")
        print("Look for:")
        print("  - New/disappeared keyboard interfaces")
        print("  - Changes in data output patterns")
        print("  - Different interval suffixes")
        
        initial_keyboards = len([d for d in [evdev.InputDevice(p) for p in evdev.list_devices()] if "TEMPerHUM" in d.name])
        print(f"Initial keyboard interfaces: {initial_keyboards}")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            current_keyboards = len([d for d in [evdev.InputDevice(p) for p in evdev.list_devices()] if "TEMPerHUM" in d.name])
            if current_keyboards != initial_keyboards:
                print(f"🎉 INTERFACE CHANGE! {initial_keyboards} → {current_keyboards}")
                return True
            time.sleep(0.5)
            print(".", end="", flush=True)
        
        print(f"\nNo interface changes detected")
        return False
    
    def run_separation_test(self):
        """Run the interface separation test"""
        print("🔀 INTERFACE SEPARATION TEST")
        print("=" * 40)
        print("Theory: One interface = output, other = control")
        print()
        
        # Step 1: Find all sensor interfaces
        sensors = self.find_sensors()
        if not sensors:
            print("❌ No sensors found!")
            return False
        
        print(f"📡 Found {len(sensors)} physical sensors:")
        for i, (base_path, interfaces) in enumerate(sensors.items(), 1):
            print(f"  Sensor {i} ({base_path}): Interfaces {list(interfaces.keys())}")
        
        # Step 2: Identify active (output) interfaces
        print(f"\n📋 Identifying active output interfaces...")
        active_interfaces = self.find_active_keyboard_interfaces()
        
        for usb_path, active_nums in active_interfaces.items():
            print(f"  {usb_path}: Active interfaces {active_nums}")
        
        # Step 3: Test control commands on inactive interfaces
        success = False
        for i, (usb_path, interfaces) in enumerate(sensors.items(), 1):
            sensor_name = f"Sensor-{i}"
            
            if self.test_control_on_inactive_interface(sensor_name, usb_path, interfaces, active_interfaces):
                # Monitor for changes after sending commands
                changes_detected = self.monitor_for_changes(8)
                
                if changes_detected:
                    print(f"✅ {sensor_name} responded to control commands!")
                    success = True
                else:
                    print(f"⚠️ No visible changes for {sensor_name}")
        
        if success:
            print(f"\n🎉 SUCCESS! Found working control interface!")
        else:
            print(f"\n❌ No control interface responded")
            print("Possible reasons:")
            print("  - Wrong command format")
            print("  - Need different timing")
            print("  - Commands work but changes not immediately visible")
        
        return success

def main():
    test = InterfaceSeparationTest()
    test.run_separation_test()

if __name__ == "__main__":
    main()