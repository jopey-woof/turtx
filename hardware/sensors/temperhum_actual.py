#!/usr/bin/env python3
"""
Actual TEMPerHUM Reader - Reads from real sensors
"""

import json
import sys
import time
import os
import struct

def read_temperhum_actual():
    """Actually read from TEMPerHUM sensors"""
    try:
        # Try each HID device
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            try:
                with open(hidraw, 'rb') as device:
                    # Try to read data
                    data = device.read(8)
                    if len(data) >= 8:
                        # Parse TEMPerHUM data format
                        temp_raw = struct.unpack("<h", data[2:4])[0]
                        humidity_raw = struct.unpack("<H", data[4:6])[0]
                        
                        # Convert to actual values
                        temperature_c = temp_raw / 100.0
                        humidity_percent = humidity_raw / 100.0
                        
                        # Return actual values regardless of range
                        return {
                            "temperature_celsius": round(temperature_c, 1),
                            "temperature_fahrenheit": round(temperature_c * 9/5 + 32, 1),
                            "humidity_percent": round(humidity_percent, 1),
                            "status": "success",
                            "device": hidraw,
                            "raw_temp": temp_raw,
                            "raw_humidity": humidity_raw
                        }
            except Exception as e:
                continue
        
        # If we get here, we couldn't read from any device
        return {"error": "Could not read from any TEMPerHUM device", "status": "no_data"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_actual()
    print(json.dumps(result)) 