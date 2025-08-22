#!/usr/bin/env python3
"""
Simple TemperhUM Activation Test - Try different interfaces and commands
"""
import hid
import time
import evdev
import sys

def test_all_activation_methods():
    """Test all possible activation methods"""
    print("🔍 SIMPLE ACTIVATION TEST")
    print("=" * 30)
    
    # Get sensors
    hid_devices = hid.enumerate(0x3553, 0xa001)
    if not hid_devices:
        print("❌ No sensors found!")
        return
    
    print(f"Found {len(hid_devices)} HID interfaces")
    
    # Different command formats to try
    commands = {
        "Standard Caps Lock": [0x00, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00],
        "Alt Caps Lock 1": [0x02, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        "Alt Caps Lock 2": [0x00, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00, 0x00],
        "Raw Caps Lock": [0x39, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        "Boot Protocol": [0x01, 0x02, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00],
    }
    
    release_cmd = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    
    # Try each interface with each command
    for i, device_info in enumerate(hid_devices):
        path = device_info['path']
        interface = device_info['interface_number']
        
        print(f"\n📱 Interface {i}: {path.decode()} (Interface {interface})")
        
        for cmd_name, cmd in commands.items():
            print(f"  Testing {cmd_name}...")
            
            try:
                device = hid.device()
                device.open_path(path)
                
                # Send command
                result = device.write(cmd)
                print(f"    Sent: {result} bytes")
                
                # Hold for 1 second
                time.sleep(1.0)
                
                # Send release
                device.write(release_cmd)
                device.close()
                
                print(f"    ✓ Command sequence completed")
                
                # Quick check for new input devices
                time.sleep(0.5)
                evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
                temperhum_keyboards = [d for d in evdev_devices if "TEMPerHUM" in d.name]
                
                if temperhum_keyboards:
                    print(f"    🎉 KEYBOARD INTERFACE FOUND!")
                    for kbd in temperhum_keyboards:
                        print(f"      {kbd.path}: {kbd.name}")
                    return True  # Success!
                
            except Exception as e:
                print(f"    ❌ Failed: {e}")
        
        print(f"  Interface {i} completed")
    
    print("\n❌ No activation method worked")
    return False

def main():
    success = test_all_activation_methods()
    
    if success:
        print("\n✅ Sensor activated! Now checking for data...")
        
        # Quick data monitoring
        evdev_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        temperhum_keyboards = [d for d in evdev_devices if "TEMPerHUM" in d.name]
        
        if temperhum_keyboards:
            print(f"Monitoring {len(temperhum_keyboards)} keyboard(s) for 5 seconds...")
            
            # Simple monitoring
            import threading
            from queue import Queue, Empty
            
            data_queue = Queue()
            
            def listen(device):
                try:
                    for event in device.read_loop():
                        if event.type == evdev.ecodes.EV_KEY:
                            key_event = evdev.categorize(event)
                            if key_event.keystate == key_event.key_down:
                                data_queue.put(key_event.scancode)
                except:
                    pass
            
            # Start listeners
            threads = []
            for device in temperhum_keyboards:
                thread = threading.Thread(target=listen, args=(device,), daemon=True)
                thread.start()
                threads.append(thread)
            
            # Monitor
            start_time = time.time()
            while time.time() - start_time < 5:
                try:
                    scancode = data_queue.get(timeout=0.1)
                    print(f"Key: {scancode}")
                except Empty:
                    continue
            
            print("Monitoring complete")
    else:
        print("\n❌ Could not activate sensors")

if __name__ == "__main__":
    main()