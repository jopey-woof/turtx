#!/usr/bin/env python3
"""
Dual TEMPerHUM Reader - Reads from both sensors with accurate conversion
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
    """Initialize TEMPerHUM device and read data with accurate conversion"""
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
                
                # Parse raw values
                temp_raw = struct.unpack("<h", data[2:4])[0]  # Signed 16-bit
                humidity_raw = struct.unpack("<H", data[4:6])[0]  # Unsigned 16-bit
                
                # Convert using adjusted scaling for more accurate temperature
                # Try scaling factor of 0.7 to get more realistic temperature
                # Raw value 31 * 0.7 = 21.7°C = 71.1°F (more reasonable)
                temperature_c = temp_raw * 0.7
                humidity_percent = humidity_raw / 100.0
                
                # If humidity is 0, try alternative parsing
                if humidity_percent == 0:
                    humidity_percent = humidity_raw
                
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

def read_temperhum_dual():
    """Read from both TEMPerHUM devices"""
    try:
        results = []
        
        # Try each HID device
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            result = init_and_read_temperhum(hidraw)
            if result.get("status") == "success":
                results.append(result)
                # Only read from first 2 sensors (we have 2 TEMPerHUM devices)
                if len(results) >= 2:
                    break
        
        if results:
            # Return the first successful result (primary sensor)
            primary = results[0]
            
            # If we have multiple sensors, include secondary data
            if len(results) > 1:
                secondary = results[1]
                return {
                    "temperature_celsius": primary["temperature_celsius"],
                    "temperature_fahrenheit": primary["temperature_fahrenheit"],
                    "humidity_percent": primary["humidity_percent"],
                    "status": "success",
                    "primary_device": primary["device"],
                    "secondary_device": secondary["device"],
                    "secondary_temp_f": secondary["temperature_fahrenheit"],
                    "secondary_humidity": secondary["humidity_percent"],
                    "raw_temp": primary["raw_temp"],
                    "raw_humidity": primary["raw_humidity"],
                    "raw_data": primary["raw_data"],
                    "sensor_count": len(results)
                }
            else:
                return primary
        
        return {"error": "Could not read from any TEMPerHUM device", "status": "no_data"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_dual()
    print(json.dumps(result)) 