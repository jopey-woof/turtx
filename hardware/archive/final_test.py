#!/usr/bin/env python3
"""
Final test to determine current sensor state
"""
import evdev
import time
import threading
from queue import Queue, Empty

def main():
    print("🔍 FINAL SENSOR STATE TEST")
    print("=" * 35)
    
    print("Current situation:")
    print("- USB sensors detected: ✅")
    print("- HID interfaces accessible: ✅") 
    print("- Input devices visible: ❌")
    print()
    
    print("This suggests the HID generic driver is not binding to the sensors.")
    print("This could be because:")
    print("1. The previous udev rule effects are still lingering")
    print("2. The sensors need physical reconnection") 
    print("3. There's a deeper kernel driver issue")
    print()
    
    print("🧪 MANUAL TEST:")
    print("Please try the following steps:")
    print()
    print("STEP 1: Physical reconnection")
    print("- Unplug both USB sensors")
    print("- Wait 5 seconds")
    print("- Plug them back in")
    print("- Wait 3 seconds")
    print()
    
    print("STEP 2: Check if they appear as input devices")
    input("Press Enter after reconnecting the sensors...")
    
    # Check for input devices
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        temperhum_devices = [d for d in devices if "TEMPerHUM" in d.name]
        
        print(f"\n📋 Input devices found: {len(temperhum_devices)}")
        
        if temperhum_devices:
            print("✅ SUCCESS! TemperhUM devices are now visible:")
            for device in temperhum_devices:
                print(f"  {device.path}: {device.name}")
            
            print("\nSTEP 3: Manual activation test")
            print("Now try manually pressing Caps Lock on one sensor for 1 second...")
            print("If it starts typing data, the sensors are working normally!")
            
            # Quick monitoring
            print("\nMonitoring for 10 seconds (press Ctrl+C to stop early):")
            monitor_briefly(temperhum_devices)
            
        else:
            print("❌ Still no TemperhUM input devices found.")
            print("\nPossible solutions:")
            print("1. Try a system reboot")
            print("2. Check if sensors work on another computer")
            print("3. The sensors might need a different activation sequence")
            print("4. There could be a hardware issue")
            
    except Exception as e:
        print(f"❌ Error checking devices: {e}")

def monitor_briefly(devices):
    """Brief monitoring for sensor data"""
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
            for event in device.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    if key_event.keystate == key_event.key_down:
                        char = keycode_map.get(key_event.scancode)
                        if char:
                            data_queue.put(char)
        except:
            pass
    
    # Start listeners
    threads = []
    for device in devices:
        thread = threading.Thread(target=listen_device, args=(device,), daemon=True)
        thread.start()
        threads.append(thread)
    
    # Monitor
    line_buffer = ""
    start_time = time.time()
    data_received = False
    
    try:
        while time.time() - start_time < 10:
            try:
                char = data_queue.get(timeout=0.5)
                data_received = True
                
                if char == '\n':
                    if line_buffer:
                        print(f"📊 SENSOR DATA: {line_buffer}")
                        line_buffer = ""
                else:
                    line_buffer += char
                    print(char, end='', flush=True)
                    
            except Empty:
                continue
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    
    if data_received:
        print(f"\n✅ SUCCESS! Sensor data received!")
    else:
        print(f"\n⚠️ No data received. Try pressing Caps Lock on a sensor.")

if __name__ == "__main__":
    main()