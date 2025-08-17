#!/usr/bin/env python3
"""
TEMPerHUM Reader using hidapi - Proper HID device communication
"""

import json
import sys
import time
import struct

def read_temperhum_hidapi():
    """Read from TEMPerHUM using hidapi library"""
    try:
        # Try to import hidapi
        try:
            import hid
        except ImportError:
            return {"error": "hidapi not installed. Install with: pip3 install hidapi", "status": "no_hidapi"}
        
        # TEMPerHUM vendor and product IDs
        VENDOR_ID = 0x3553
        PRODUCT_ID = 0xa001
        
        # Find TEMPerHUM devices
        devices = []
        for device in hid.enumerate(VENDOR_ID, PRODUCT_ID):
            devices.append(device)
        
        if not devices:
            return {"error": "No TEMPerHUM devices found", "status": "no_devices"}
        
        # Try to read from the first device
        try:
            device = hid.device()
            device.open(VENDOR_ID, PRODUCT_ID)
            
            # Set non-blocking mode
            device.set_nonblocking(1)
            
            # Try to read data
            start_time = time.time()
            data = b''
            
            while len(data) < 8 and (time.time() - start_time) < 2.0:
                try:
                    chunk = device.read(8 - len(data))
                    if chunk:
                        data += bytes(chunk)
                    else:
                        time.sleep(0.01)
                except Exception:
                    time.sleep(0.01)
            
            device.close()
            
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
                    "device_count": len(devices),
                    "raw_temp": temp_raw,
                    "raw_humidity": humidity_raw
                }
            else:
                return {"error": "Insufficient data from device", "status": "insufficient_data"}
                
        except Exception as e:
            return {"error": f"Device read error: {str(e)}", "status": "device_error"}
            
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_hidapi()
    print(json.dumps(result)) 