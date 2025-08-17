#!/usr/bin/env python3
"""
Proper TEMPerHUM Initialization and Reading
Initializes TEMPerHUM devices and reads real data
"""

import json
import sys
import time
import os
import struct

def init_temperhum_device(device_path):
    """Initialize a TEMPerHUM device"""
    try:
        with open(device_path, 'rb+') as device:
            # Send initialization commands
            # Command 1: Reset device
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.1)
            
            # Command 2: Start continuous reading
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.1)
            
            # Command 3: Request data
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.2)
            
            return True
    except Exception as e:
        return False

def read_temperhum_data(device_path):
    """Read data from initialized TEMPerHUM device"""
    try:
        with open(device_path, 'rb') as device:
            # Read data with timeout
            start_time = time.time()
            data = b''
            
            while len(data) < 8 and (time.time() - start_time) < 2.0:
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
                    "device": device_path,
                    "raw_temp": temp_raw,
                    "raw_humidity": humidity_raw
                }
    except Exception as e:
        return None

def read_temperhum_init():
    """Initialize and read from TEMPerHUM sensors"""
    try:
        # Try each HID device
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            # Initialize the device
            if init_temperhum_device(hidraw):
                # Try to read data
                result = read_temperhum_data(hidraw)
                if result:
                    return result
                
                # If first read failed, try again after a delay
                time.sleep(0.5)
                result = read_temperhum_data(hidraw)
                if result:
                    return result
        
        # If we get here, try a different approach - direct read without init
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            try:
                with open(hidraw, 'rb') as device:
                    # Try to read whatever is available
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
        
        return {"error": "Could not initialize or read from any TEMPerHUM device", "status": "no_data"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_init()
    print(json.dumps(result)) 