#!/usr/bin/env python3
"""
Corrected TEMPerHUM Reader - Based on working results
"""

import json
import sys
import time
import os
import struct
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def init_and_read_temperhum(device_path):
    """Initialize TEMPerHUM device and read data"""
    try:
        # Initialize the device first
        with open(device_path, 'rb+') as device:
            # Send initialization sequence
            # Command 1: Reset device
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.1)
            
            # Command 2: Start continuous reading
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.1)
            
            # Command 3: Request data
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.2)
        
        # Now try to read with timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(2)  # 2 second timeout
        
        with open(device_path, 'rb') as device:
            # Read 8 bytes
            data = device.read(8)
            signal.alarm(0)  # Cancel timeout
            
            if len(data) >= 8:
                # Debug: show raw data
                raw_hex = ' '.join([f'{b:02x}' for b in data])
                
                # Try different parsing methods based on the working results
                # Method 1: Direct byte values
                temp_raw = data[2]  # Single byte temperature
                humidity_raw = data[4]  # Single byte humidity
                
                # Convert to actual values (adjust scaling based on results)
                temperature_c = temp_raw - 40  # Common offset for temperature sensors
                humidity_percent = humidity_raw
                
                # Sanity check - if values are reasonable
                if 0 <= temperature_c <= 50 and 0 <= humidity_percent <= 100:
                    return {
                        "temperature_celsius": round(temperature_c, 1),
                        "temperature_fahrenheit": round(temperature_c * 9/5 + 32, 1),
                        "humidity_percent": round(humidity_percent, 1),
                        "status": "success",
                        "device": device_path,
                        "raw_temp": temp_raw,
                        "raw_humidity": humidity_raw,
                        "raw_data": raw_hex
                    }
                else:
                    # Try alternative parsing
                    temp_raw_alt = struct.unpack("<h", data[2:4])[0]
                    humidity_raw_alt = struct.unpack("<H", data[4:6])[0]
                    
                    # Different scaling
                    temperature_c_alt = temp_raw_alt / 256.0
                    humidity_percent_alt = humidity_raw_alt / 256.0
                    
                    return {
                        "temperature_celsius": round(temperature_c_alt, 1),
                        "temperature_fahrenheit": round(temperature_c_alt * 9/5 + 32, 1),
                        "humidity_percent": round(humidity_percent_alt, 1),
                        "status": "success",
                        "device": device_path,
                        "raw_temp": temp_raw_alt,
                        "raw_humidity": humidity_raw_alt,
                        "raw_data": raw_hex,
                        "method": "alternative"
                    }
            else:
                return {"error": f"Insufficient data from {device_path}", "status": "insufficient_data"}
                
    except TimeoutError:
        return {"error": f"Timeout reading from {device_path}", "status": "timeout"}
    except Exception as e:
        return {"error": f"Error with {device_path}: {str(e)}", "status": "error"}

def read_temperhum_correct():
    """Read from TEMPerHUM devices with corrected parsing"""
    try:
        # Try each HID device
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            result = init_and_read_temperhum(hidraw)
            if result.get("status") == "success":
                return result
        
        return {"error": "Could not read from any TEMPerHUM device", "status": "no_data"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_correct()
    print(json.dumps(result)) 