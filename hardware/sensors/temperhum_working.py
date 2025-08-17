#!/usr/bin/env python3
"""
Working TEMPerHUM USB Sensor Reader
Reads temperature and humidity from PCsensor TEMPerHUM devices without hanging
"""

import json
import sys
import time
import select
import os

def read_temperhum_working():
    """Read temperature and humidity with proper timeout and error handling"""
    try:
        # Check if device exists and is readable
        if not os.path.exists('/dev/hidraw1'):
            return {"error": "Device not found", "status": "no_device"}
        
        # Try to read with timeout
        with open('/dev/hidraw1', 'rb') as device:
            # Set non-blocking mode
            fd = device.fileno()
            os.set_blocking(fd, False)
            
            # Try to read with timeout
            ready, _, _ = select.select([device], [], [], 2.0)  # 2 second timeout
            
            if not ready:
                return {"error": "Device timeout", "status": "timeout"}
            
            data = device.read(8)
            if len(data) >= 8:
                # Parse TEMPerHUM data format
                temp_raw = int.from_bytes(data[2:4], byteorder='little', signed=True)
                humidity_raw = int.from_bytes(data[4:6], byteorder='little', signed=False)
                
                # Convert to actual values
                temperature_c = temp_raw / 100.0
                humidity_percent = humidity_raw / 100.0
                
                # Sanity checks
                if -40 <= temperature_c <= 80 and 0 <= humidity_percent <= 100:
                    return {
                        "temperature_celsius": round(temperature_c, 1),
                        "temperature_fahrenheit": round(temperature_c * 9/5 + 32, 1),
                        "humidity_percent": round(humidity_percent, 1),
                        "status": "success"
                    }
                else:
                    return {"error": "Invalid sensor values", "status": "invalid_data"}
            else:
                return {"error": "Insufficient data", "status": "insufficient_data"}
                
    except PermissionError:
        return {"error": "Permission denied", "status": "permission_error"}
    except Exception as e:
        return {"error": str(e), "status": "exception"}
    
    return {"error": "Unknown error", "status": "unknown"}

if __name__ == "__main__":
    result = read_temperhum_working()
    print(json.dumps(result)) 