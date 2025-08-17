import os
import time
import struct
import sys

def init_and_read_temperhum_direct(device_path):
    print(f"Attempting to read from device: {device_path}")
    try:
        if not os.path.exists(device_path):
            print(f"Error: Device path {device_path} does not exist.")
            return None

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

            # Read 8 bytes from the device
            data = device.read(8)
            
            raw_hex = ' '.join([f'{b:02x}' for b in data])
            print(f"READ RAW DATA from {device_path} (length {len(data)}): {raw_hex}")
            
            if len(data) >= 8:
                # Parse raw values
                temp_raw = struct.unpack("<h", data[2:4])[0]  # Signed 16-bit
                humidity_raw = struct.unpack("<H", data[4:6])[0]  # Unsigned 16-bit
                
                temperature_c = temp_raw / 100.0 
                humidity_percent = humidity_raw / 100.0 
                
                if humidity_percent == 0 and humidity_raw != 0:
                    humidity_percent = float(humidity_raw) 
                
                print(f"Parsed - Temp Raw: {temp_raw}, Humidity Raw: {humidity_raw}")
                print(f"Converted - Temp C: {temperature_c}, Humidity %: {humidity_percent}")
                
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
                print(f"Warning: Insufficient data from {device_path}. Read {len(data)} bytes, expected 8.")
                return {"status": "error", "message": "Insufficient data"}
                
    except FileNotFoundError:
        print(f"Error: Device {device_path} not found. Check if it's connected and path is correct.")
        return {"status": "error", "message": "Device not found"}
    except PermissionError:
        print(f"Error: Permission denied for {device_path}. Check device permissions and Docker container device mapping.")
        return {"status": "error", "message": "Permission denied"}
    except Exception as e:
        print(f"An unexpected error occurred with {device_path}: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    devices = ["/dev/hidraw1", "/dev/hidraw2"]
    for device in devices:
        result = init_and_read_temperhum_direct(device)
        print(f"Result for {device}: {result}\n")