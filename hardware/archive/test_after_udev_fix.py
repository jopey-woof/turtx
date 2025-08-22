#!/usr/bin/env python3
"""
Test TemperhUM sensors after fixing udev rules
"""
import evdev
import time

def main():
    print("🔧 TESTING AFTER UDEV RULE REMOVAL")
    print("=" * 40)
    
    print("The problematic udev rules have been removed.")
    print("These rules were preventing the sensors from appearing as keyboards.")
    print()
    
    # Check current state
    print("📋 Current input devices:")
    try:
        all_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        temperhum_devices = [d for d in all_devices if "TEMPerHUM" in d.name]
        
        print(f"Total input devices: {len(all_devices)}")
        print(f"TemperhUM devices: {len(temperhum_devices)}")
        
        if temperhum_devices:
            print("\n✅ TemperhUM keyboard interfaces found:")
            for device in temperhum_devices:
                print(f"  {device.path}: {device.name}")
                print(f"    Physical: {device.phys}")
        else:
            print("\n⚠️ No TemperhUM keyboard interfaces found yet.")
            print("You may need to:")
            print("1. Physically disconnect and reconnect the USB sensors")
            print("2. Or try manually pressing Caps Lock on a sensor")
    
    except Exception as e:
        print(f"❌ Error checking devices: {e}")
    
    print(f"\n📝 WHAT WAS FIXED:")
    print("- Removed udev rule that unbinded HID generic driver")
    print("- Removed permission rules that weren't needed")
    print("- Sensors should now work normally as keyboards when activated")
    
    print(f"\n🧪 NEXT STEPS:")
    print("1. Try manually pressing Caps Lock on a sensor for 1 second")
    print("2. Check if it starts typing data to this terminal")
    print("3. If not, try unplugging and reconnecting the USB sensors")

if __name__ == "__main__":
    main()