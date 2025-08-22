#!/usr/bin/env python3
"""
Simple test to verify evdev can read from TEMPerHUM devices
"""

import os
import sys
from evdev import InputDevice, categorize, ecodes

def test_device(device_path):
    print(f"Testing device: {device_path}")
    try:
        device = InputDevice(device_path)
        print(f"✅ Opened device: {device.name}")
        print(f"📋 Device info: {device.info}")
        print(f"📋 Device capabilities: {device.capabilities()}")
        
        # Try to read a few events
        print("🔍 Reading events (press Ctrl+C to stop)...")
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                print(f"Key event: {key_event}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    if os.geteuid() != 0:
        print("❌ Must run with sudo")
        sys.exit(1)
        
    print("🐢 Testing TEMPerHUM input devices")
    print("=" * 40)
    
    devices = ['/dev/input/event3', '/dev/input/event4']
    
    for device_path in devices:
        test_device(device_path)
        print()

if __name__ == "__main__":
    main() 