#!/usr/bin/env python3
"""
TemperhUM Sensor Analysis Report - Complete findings and recommendations
"""
import hid
import evdev
import subprocess
import os

def generate_report():
    print("🔬 TEMPERHUM SENSOR ANALYSIS REPORT")
    print("=" * 50)
    
    # Hardware Detection
    print("\n1️⃣ HARDWARE DETECTION:")
    print("-" * 25)
    
    # USB Detection
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        temperhum_lines = [line for line in result.stdout.split('\n') if '3553:a001' in line]
        print(f"USB Devices Found: {len(temperhum_lines)}")
        for line in temperhum_lines:
            print(f"  {line.strip()}")
    except:
        print("❌ Could not run lsusb")
    
    # HID Interface Detection
    try:
        hid_devices = hid.enumerate(0x3553, 0xa001)
        sensor_groups = {}
        
        print(f"\nHID Interfaces Found: {len(hid_devices)}")
        for device in hid_devices:
            path = device['path'].decode()
            interface_num = device['interface_number']
            base_path = path.split(':')[0]
            
            if base_path not in sensor_groups:
                sensor_groups[base_path] = []
            sensor_groups[base_path].append(interface_num)
            
            print(f"  {path} (Interface {interface_num})")
        
        print(f"\nPhysical Sensors: {len(sensor_groups)}")
        for base_path, interfaces in sensor_groups.items():
            print(f"  {base_path}: Interfaces {interfaces}")
            
    except Exception as e:
        print(f"❌ HID enumeration failed: {e}")
        sensor_groups = {}
    
    # USB Interface Analysis
    print("\n2️⃣ USB INTERFACE ANALYSIS:")
    print("-" * 30)
    
    try:
        # Get detailed USB info
        for dev_num in [2, 3]:  # Based on lsusb output
            try:
                result = subprocess.run(
                    ['lsusb', '-v', '-d', '3553:a001', '-s', f'1:{dev_num}'],
                    capture_output=True, text=True, stderr=subprocess.DEVNULL
                )
                if result.stdout:
                    lines = result.stdout.split('\n')
                    interface_lines = [line for line in lines if 'bInterfaceNumber' in line or 'bInterfaceProtocol' in line]
                    print(f"Device 1:{dev_num} interfaces:")
                    for line in interface_lines:
                        print(f"  {line.strip()}")
            except:
                pass
    except:
        print("❌ Could not get detailed USB info")
    
    # Current Keyboard Interfaces
    print("\n3️⃣ CURRENT KEYBOARD INTERFACES:")
    print("-" * 35)
    
    try:
        evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        temperhum_keyboards = [d for d in evdev_devices if "TEMPerHUM" in d.name]
        
        print(f"TemperhUM Keyboards Found: {len(temperhum_keyboards)}")
        for device in temperhum_keyboards:
            print(f"  {device.path}: {device.name}")
            print(f"    Physical: {device.phys}")
            
    except Exception as e:
        print(f"❌ Keyboard detection failed: {e}")
    
    # Test Results Summary
    print("\n4️⃣ TEST RESULTS SUMMARY:")
    print("-" * 30)
    
    print("✅ WORKING:")
    print("  - USB device detection (2 sensors found)")
    print("  - HID interface enumeration (4 interfaces total)")
    print("  - HID device communication (commands sent successfully)")
    print("  - Dual interface structure identified")
    
    print("\n❌ NOT WORKING:")
    print("  - Sensor activation (no keyboard interfaces appear)")
    print("  - Data output capture (no typing detected)")
    
    # Analysis and Recommendations
    print("\n5️⃣ ANALYSIS & RECOMMENDATIONS:")
    print("-" * 40)
    
    print("🔍 FINDINGS:")
    print("  - Each sensor has 2 HID interfaces (0 and 1)")
    print("  - Interface 0: Keyboard protocol (likely data output)")
    print("  - Interface 1: Mouse protocol (likely control input)")
    print("  - HID commands are accepted but don't trigger activation")
    
    print("\n💡 POSSIBLE ISSUES:")
    print("  1. Command format incorrect for Linux")
    print("  2. Need different activation sequence")
    print("  3. Driver/permission issues")
    print("  4. Sensors might need manual button press first")
    print("  5. Different HID report descriptor on Linux")
    
    print("\n🛠️ NEXT STEPS TO TRY:")
    print("  1. Manual button press test:")
    print("     - Physically press Caps Lock on sensor")
    print("     - Check if keyboard interface appears")
    print("     - Monitor for data output")
    
    print("\n  2. Different command formats:")
    print("     - Try sending to Interface 0 instead of Interface 1")
    print("     - Try different HID report formats")
    print("     - Try raw HID descriptor analysis")
    
    print("\n  3. Permission/driver investigation:")
    print("     - Check udev rules")
    print("     - Try running as root")
    print("     - Check kernel HID driver logs")
    
    print("\n  4. Alternative activation methods:")
    print("     - Try Num Lock commands")
    print("     - Try combination key sequences")
    print("     - Investigate Windows vs Linux HID differences")

def main():
    generate_report()
    
    print("\n" + "=" * 50)
    print("📋 MANUAL TESTING INSTRUCTIONS:")
    print("=" * 50)
    
    print("\n🔧 TEST 1 - Manual Button Press:")
    print("1. Physically press and hold Caps Lock on a sensor for 1 second")
    print("2. Run: python3 -c \"import evdev; print([d.name for d in [evdev.InputDevice(p) for p in evdev.list_devices()] if 'TEMPerHUM' in d.name])\"")
    print("3. If keyboards appear, run a simple listener to capture data")
    
    print("\n🔧 TEST 2 - Root Permissions:")
    print("1. Try running the activation script as root")
    print("2. Check if permission elevation helps")
    
    print("\n🔧 TEST 3 - Different Interface:")
    print("1. Try sending commands to Interface 0 instead of Interface 1")
    print("2. Interface 0 might be the control interface on some models")
    
    print("\n📞 If manual button press works but programmatic doesn't:")
    print("   - The sensors are functional")
    print("   - Issue is with HID command format/protocol")
    print("   - Need to analyze HID descriptors or try different commands")

if __name__ == "__main__":
    main()