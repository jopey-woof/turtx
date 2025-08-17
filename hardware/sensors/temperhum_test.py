#!/usr/bin/env python3
"""
Simple TEMPerHUM Test - Check if devices respond at all
"""

import json
import sys
import time
import os
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def test_hid_device(device_path):
    """Test if HID device responds at all"""
    try:
        # Set a very short timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1)  # 1 second timeout
        
        with open(device_path, 'rb') as device:
            # Try to read just 1 byte
            data = device.read(1)
            signal.alarm(0)  # Cancel timeout
            
            if data:
                return {"status": "responds", "device": device_path, "data_length": len(data)}
            else:
                return {"status": "no_data", "device": device_path}
                
    except TimeoutError:
        return {"status": "timeout", "device": device_path}
    except Exception as e:
        return {"status": "error", "device": device_path, "error": str(e)}

def test_temperhum_devices():
    """Test all TEMPerHUM devices"""
    results = []
    
    for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
        if os.path.exists(hidraw):
            result = test_hid_device(hidraw)
            results.append(result)
    
    return {
        "test_results": results,
        "total_devices": len(results),
        "timestamp": time.time()
    }

if __name__ == "__main__":
    result = test_temperhum_devices()
    print(json.dumps(result)) 