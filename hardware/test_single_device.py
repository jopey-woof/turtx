#!/usr/bin/env python3
"""
Test individual TEMPerHUM devices to see what errors occur
"""

import os
import sys
from evdev import InputDevice, categorize, ecodes

def test_device(device_path, device_name):
    print(f"\n🔍 Testing {device_name}: {device_path}")
    try:
        device = InputDevice(device_path)
        print(f"✅ Opened device: {device.name}")
        print(f"📋 Device info: {device.info}")
        
        # Try to read a few events
        print("🔍 Reading events (press Ctrl+C to stop)...")
        event_count = 0
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                print(f"Key event: {key_event}")
                event_count += 1
                if event_count > 10:  # Just read a few events
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    if os.geteuid() != 0:
        print("❌ Must run with sudo")
        sys.exit(1)
        
    print("🐢 Testing individual TEMPerHUM devices")
    print("=" * 40)
    
    devices = [
        ('/dev/input/event3', 'Sensor 1'),
        ('/dev/input/event4', 'Sensor 2')
    ]
    
    for device_path, device_name in devices:
        test_device(device_path, device_name)

if __name__ == "__main__":
    main() 