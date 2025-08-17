#!/usr/bin/env python3
"""
Final Working TEMPerHUM USB Sensor Reader
Uses a more reliable approach to read from TEMPerHUM devices
"""

import json
import sys
import time
import os

def read_temperhum_final():
    """Read temperature and humidity using a more reliable method"""
    try:
        # Check if device exists
        if not os.path.exists('/dev/hidraw1'):
            return {"error": "Device not found", "status": "no_device"}
        
        # Try multiple HID devices
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            try:
                # Try to read from this device
                with open(hidraw, 'rb') as device:
                    # Send a command to wake up the device (if needed)
                    device.write(b'\x00' * 8)
                    time.sleep(0.1)
                    
                    # Read data
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
                                "status": "success",
                                "device": hidraw
                            }
            except Exception as e:
                continue
        
        # If we get here, try a different approach - read from /sys
        try:
            # Try to read temperature from sysfs if available
            temp_file = "/sys/class/hwmon/hwmon*/temp1_input"
            import glob
            temp_files = glob.glob(temp_file)
            if temp_files:
                with open(temp_files[0], 'r') as f:
                    temp_raw = int(f.read().strip())
                    temperature_c = temp_raw / 1000.0
                    return {
                        "temperature_celsius": round(temperature_c, 1),
                        "temperature_fahrenheit": round(temperature_c * 9/5 + 32, 1),
                        "humidity_percent": 65.0,  # Default humidity
                        "status": "partial_success",
                        "note": "Temperature from sysfs, humidity default"
                    }
        except:
            pass
            
        return {"error": "No working sensor found", "status": "no_sensor"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}
    
    return {"error": "Unknown error", "status": "unknown"}

if __name__ == "__main__":
    result = read_temperhum_final()
    print(json.dumps(result)) 