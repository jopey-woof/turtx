#!/usr/bin/env python3
"""
TEMPerHUM Debug - Test different conversion methods
"""

import json
import sys
import time
import os
import struct
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def test_conversions(raw_temp, raw_humidity):
    """Test different conversion methods"""
    conversions = []
    
    # Method 1: Standard TEMPerHUM (divide by 100)
    temp_c1 = raw_temp / 100.0
    humidity1 = raw_humidity / 100.0
    conversions.append({
        "method": "standard_divide_100",
        "temp_c": temp_c1,
        "temp_f": temp_c1 * 9/5 + 32,
        "humidity": humidity1
    })
    
    # Method 2: Alternative scaling (divide by 256)
    temp_c2 = raw_temp / 256.0
    humidity2 = raw_humidity / 256.0
    conversions.append({
        "method": "divide_256",
        "temp_c": temp_c2,
        "temp_f": temp_c2 * 9/5 + 32,
        "humidity": humidity2
    })
    
    # Method 3: Offset method (divide by 100, then offset)
    temp_c3 = (raw_temp / 100.0) - 40
    humidity3 = raw_humidity / 100.0
    conversions.append({
        "method": "divide_100_offset_40",
        "temp_c": temp_c3,
        "temp_f": temp_c3 * 9/5 + 32,
        "humidity": humidity3
    })
    
    # Method 4: Direct byte value
    temp_c4 = raw_temp
    humidity4 = raw_humidity
    conversions.append({
        "method": "direct_byte_value",
        "temp_c": temp_c4,
        "temp_f": temp_c4 * 9/5 + 32,
        "humidity": humidity4
    })
    
    # Method 5: Different scaling factor
    temp_c5 = raw_temp / 10.0
    humidity5 = raw_humidity / 10.0
    conversions.append({
        "method": "divide_10",
        "temp_c": temp_c5,
        "temp_f": temp_c5 * 9/5 + 32,
        "humidity": humidity5
    })
    
    return conversions

def read_temperhum_debug():
    """Read from TEMPerHUM and test all conversion methods"""
    try:
        # Try each HID device
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            try:
                # Initialize the device
                with open(hidraw, 'rb+') as device:
                    device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
                    time.sleep(0.1)
                    device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
                    time.sleep(0.1)
                    device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
                    time.sleep(0.2)
                
                # Read data
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(2)
                
                with open(hidraw, 'rb') as device:
                    data = device.read(8)
                    signal.alarm(0)
                    
                    if len(data) >= 8:
                        raw_hex = ' '.join([f'{b:02x}' for b in data])
                        
                        # Parse raw values
                        temp_raw = struct.unpack("<h", data[2:4])[0]
                        humidity_raw = struct.unpack("<H", data[4:6])[0]
                        
                        # Test all conversion methods
                        conversions = test_conversions(temp_raw, humidity_raw)
                        
                        return {
                            "status": "success",
                            "device": hidraw,
                            "raw_temp": temp_raw,
                            "raw_humidity": humidity_raw,
                            "raw_data": raw_hex,
                            "conversions": conversions
                        }
                        
            except Exception as e:
                continue
        
        return {"error": "Could not read from any TEMPerHUM device", "status": "no_data"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_debug()
    print(json.dumps(result, indent=2)) 