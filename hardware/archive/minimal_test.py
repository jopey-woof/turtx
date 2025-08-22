#!/usr/bin/env python3
"""
Minimal TemperhUM Test - Simplest possible test
"""
import hid
import time

def main():
    print("🔍 MINIMAL SENSOR TEST")
    print("=" * 25)
    
    try:
        # Find sensors
        devices = hid.enumerate(0x3553, 0xa001)
        print(f"Found {len(devices)} HID interfaces")
        
        if not devices:
            print("❌ No sensors found")
            return
        
        # Try to activate each interface
        for i, device_info in enumerate(devices):
            path = device_info['path']
            interface = device_info['interface_number']
            
            print(f"\nTesting interface {interface}: {path.decode()}")
            
            try:
                device = hid.device()
                device.open_path(path)
                
                # Simple Caps Lock command
                caps_cmd = [0x00, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00]
                release_cmd = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                
                print("  Sending activation command...")
                device.write(caps_cmd)
                time.sleep(1)
                device.write(release_cmd)
                
                device.close()
                print("  ✓ Command sent")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print(f"\nActivation attempts completed.")
        print("If sensors activated, they should be typing data now.")
        print("Check with: python3 -c \"import evdev; print([d.name for d in [evdev.InputDevice(p) for p in evdev.list_devices()] if 'TEMPerHUM' in d.name])\"")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()