#!/usr/bin/env python3
"""
Proper TEMPerHUM Reader - Using correct protocol for popular TEMPerHUM sensors
Based on known working implementations for RPi and Arduino
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
    """Initialize TEMPerHUM device and read data using correct protocol"""
    try:
        # Initialize the device first
        with open(device_path, 'rb+') as device:
            # Send initialization sequence for TEMPerHUM
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
                
                # TEMPerHUM protocol: bytes 2-3 for temperature, bytes 4-5 for humidity
                # Temperature: signed 16-bit, divide by 100 to get Celsius
                # Humidity: unsigned 16-bit, divide by 100 to get percentage
                
                temp_raw = struct.unpack("<h", data[2:4])[0]  # Signed 16-bit
                humidity_raw = struct.unpack("<H", data[4:6])[0]  # Unsigned 16-bit
                
                # Convert using standard TEMPerHUM conversion
                temperature_c = temp_raw / 100.0
                humidity_percent = humidity_raw / 100.0
                
                # Sanity check - if values are unreasonable, try alternative parsing
                if temperature_c < -50 or temperature_c > 100 or humidity_percent < 0 or humidity_percent > 100:
                    # Try alternative parsing method
                    # Some TEMPerHUM variants use different byte order or scaling
                    temp_raw_alt = struct.unpack(">h", data[2:4])[0]  # Big-endian
                    humidity_raw_alt = struct.unpack(">H", data[4:6])[0]  # Big-endian
                    
                    temperature_c_alt = temp_raw_alt / 100.0
                    humidity_percent_alt = humidity_raw_alt / 100.0
                    
                    # Use whichever gives reasonable values
                    if -50 <= temperature_c_alt <= 100 and 0 <= humidity_percent_alt <= 100:
                        temperature_c = temperature_c_alt
                        humidity_percent = humidity_percent_alt
                        temp_raw = temp_raw_alt
                        humidity_raw = humidity_raw_alt
                
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
                return {"error": f"Insufficient data from {device_path}", "status": "insufficient_data"}
                
    except TimeoutError:
        return {"error": f"Timeout reading from {device_path}", "status": "timeout"}
    except Exception as e:
        return {"error": f"Error with {device_path}: {str(e)}", "status": "error"}

def read_temperhum_proper():
    """Read from TEMPerHUM devices using proper protocol"""
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
    result = read_temperhum_proper()
    print(json.dumps(result)) 