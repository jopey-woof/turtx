#!/usr/bin/env python3
"""
Simple TEMPerHUM Initialization - Uses known working commands
"""

import json
import sys
import time
import os
import struct

def read_temperhum_simple_init():
    """Simple initialization and read from TEMPerHUM sensors"""
    try:
        # Try each HID device
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            try:
                # Try to read directly first
                with open(hidraw, 'rb') as device:
                    # Set non-blocking mode
                    os.set_blocking(device.fileno(), False)
                    
                    # Try to read with timeout
                    start_time = time.time()
                    data = b''
                    while len(data) < 8 and (time.time() - start_time) < 1.0:
                        chunk = device.read(8 - len(data))
                        if chunk:
                            data += chunk
                        else:
                            time.sleep(0.01)
                    
                    if len(data) >= 8:
                        # Parse TEMPerHUM data format
                        temp_raw = struct.unpack("<h", data[2:4])[0]
                        humidity_raw = struct.unpack("<H", data[4:6])[0]
                        
                        # Convert to actual values
                        temperature_c = temp_raw / 100.0
                        humidity_percent = humidity_raw / 100.0
                        
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
        
        # If direct read failed, try with initialization
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            try:
                # Initialize device
                with open(hidraw, 'rb+') as device:
                    # Send initialization command
                    device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
                    time.sleep(0.2)
                
                # Now try to read
                with open(hidraw, 'rb') as device:
                    data = device.read(8)
                    if len(data) >= 8:
                        # Parse data
                        temp_raw = struct.unpack("<h", data[2:4])[0]
                        humidity_raw = struct.unpack("<H", data[4:6])[0]
                        
                        temperature_c = temp_raw / 100.0
                        humidity_percent = humidity_raw / 100.0
                        
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
        
        return {"error": "Could not read from any TEMPerHUM device", "status": "no_data"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_simple_init()
    print(json.dumps(result)) 