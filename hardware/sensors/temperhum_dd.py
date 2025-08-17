#!/usr/bin/env python3
"""
TEMPerHUM Reader using dd command - Direct device access
"""

import json
import sys
import time
import os
import subprocess
import struct

def read_temperhum_dd():
    """Read from TEMPerHUM using dd command"""
    try:
        # Try each HID device
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            try:
                # Use dd to read 8 bytes from the device
                result = subprocess.run(['dd', 'if=' + hidraw, 'bs=8', 'count=1'], 
                                      capture_output=True, text=True, timeout=3)
                
                if result.returncode == 0 and result.stdout:
                    # Convert hex output to bytes
                    hex_data = result.stdout.strip()
                    if len(hex_data) >= 16:  # At least 8 bytes in hex
                        # Parse the hex data
                        data = bytes.fromhex(hex_data[:16])
                        
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
            except subprocess.TimeoutExpired:
                continue
            except Exception as e:
                continue
        
        # If dd approach failed, try hexdump
        for hidraw in ['/dev/hidraw1', '/dev/hidraw2', '/dev/hidraw3', '/dev/hidraw4']:
            if not os.path.exists(hidraw):
                continue
                
            try:
                # Use hexdump to read data
                result = subprocess.run(['hexdump', '-C', '-n', '8', hidraw], 
                                      capture_output=True, text=True, timeout=3)
                
                if result.returncode == 0 and result.stdout:
                    # Parse hexdump output
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        # Extract hex data from hexdump output
                        hex_line = lines[0]
                        hex_parts = hex_line.split()
                        if len(hex_parts) >= 9:  # Skip address and ASCII parts
                            hex_data = ''.join(hex_parts[1:9])
                            data = bytes.fromhex(hex_data)
                            
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
            except subprocess.TimeoutExpired:
                continue
            except Exception as e:
                continue
        
        return {"error": "Could not read from any TEMPerHUM device using dd/hexdump", "status": "no_data"}
                
    except Exception as e:
        return {"error": str(e), "status": "exception"}

if __name__ == "__main__":
    result = read_temperhum_dd()
    print(json.dumps(result)) 