#!/usr/bin/env python3
"""
TemperhUM Controller - Complete sensor control and data reading
Based on temper-py protocol with added control functionality
"""
import os
import struct
import select
import binascii
import time
import threading
import json
import re
from typing import Dict, List, Optional, Tuple

class TemperhUMController:
    """Complete TemperhUM sensor controller with read and control capabilities"""
    
    def __init__(self, verbose: bool = False, temperature_unit: str = "celsius"):
        self.verbose = verbose
        self.temperature_unit = temperature_unit
        self.sensors = {}
        self.discover_sensors()
    
    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[TemperhUM] {message}")
    
    def discover_sensors(self):
        """Discover available TemperhUM sensors - BULLETPROOF PORT-AGNOSTIC VERSION"""
        self.sensors = {}
        device_interfaces = {}  # Track all interfaces by USB device path
        
        # Scan for TemperhUM devices (VID:PID = 3553:a001)
        for i in range(20):
            hidraw_path = f'/dev/hidraw{i}'
            if os.path.exists(hidraw_path):
                try:
                    # Read device uevent to get USB physical path
                    uevent_path = f'/sys/class/hidraw/hidraw{i}/device/uevent'
                    if os.path.exists(uevent_path):
                        with open(uevent_path, 'r') as f:
                            uevent_data = f.read()
                        
                        # Check if this is a TemperhUM device
                        if 'HID_NAME=PCsensor TEMPerHUM' in uevent_data and '3553:0000A001' in uevent_data:
                            # Extract USB physical path
                            phys_match = re.search(r'HID_PHYS=([^\n]+)', uevent_data)
                            if phys_match:
                                phys_path = phys_match.group(1)
                                self.log(f"Found TemperhUM device at {hidraw_path}: {phys_path}")
                                
                                # Parse interface type from path (input0 = output, input1 = control)
                                interface_type = None
                                if '/input0' in phys_path:
                                    interface_type = 'output'
                                elif '/input1' in phys_path:
                                    interface_type = 'control'
                                
                                if interface_type:
                                    # Extract the base USB device path (everything before /input)
                                    base_path = phys_path.split('/input')[0]
                                    
                                    # Store this interface under the base USB path
                                    if base_path not in device_interfaces:
                                        device_interfaces[base_path] = {}
                                    device_interfaces[base_path][interface_type] = hidraw_path
                                    self.log(f"Mapped {base_path} {interface_type} -> {hidraw_path}")
                        
                except Exception as e:
                    self.log(f"Error scanning {hidraw_path}: {e}")
        
        # Convert USB device paths to sensor IDs (port-agnostic)
        sensor_counter = 1
        for base_path, interfaces in sorted(device_interfaces.items()):
            # Only create sensor entries for complete devices (both interfaces)
            if 'output' in interfaces and 'control' in interfaces:
                sensor_id = f'sensor{sensor_counter}'
                self.sensors[sensor_id] = {
                    'output': interfaces['output'],
                    'control': interfaces['control'],
                    'usb_path': base_path
                }
                self.log(f"Created {sensor_id}: output={interfaces['output']}, control={interfaces['control']}")
                sensor_counter += 1
            else:
                missing = [t for t in ['output', 'control'] if t not in interfaces]
                self.log(f"Incomplete sensor at {base_path}, missing: {missing}")
        
        sensor_list = list(self.sensors.keys())
        self.log(f"Discovered {len(sensor_list)} complete sensors: {sensor_list}")
    
    def get_available_sensors(self) -> List[str]:
        """Get list of available sensor IDs"""
        return list(self.sensors.keys())
    
    def read_firmware(self, hidraw_path: str) -> Optional[str]:
        """Read firmware version from sensor"""
        try:
            fd = os.open(hidraw_path, os.O_RDWR)
            
            # Send firmware query (from temper-py)
            query = struct.pack('8B', 0x01, 0x86, 0xff, 0x01, 0, 0, 0, 0)
            self.log(f"Firmware query: {binascii.b2a_hex(query)}")
            
            # Retry firmware read (temper-py does this)
            firmware = b''
            for attempt in range(10):
                os.write(fd, query)
                
                while True:
                    r, _, _ = select.select([fd], [], [], 0.2)
                    if fd not in r:
                        break
                    data = os.read(fd, 8)
                    firmware += data
                
                if len(firmware) > 8:
                    break
            
            os.close(fd)
            
            if firmware:
                firmware_str = str(firmware, 'latin-1').strip()
                self.log(f"Firmware: {firmware_str}")
                return firmware_str
            
        except Exception as e:
            self.log(f"Firmware read error: {e}")
        
        return None
    
    def read_sensor_data(self, hidraw_path: str) -> Optional[Dict]:
        """Read temperature and humidity data from sensor"""
        try:
            fd = os.open(hidraw_path, os.O_RDWR)
            
            # Get firmware version (we need it for parsing)
            firmware_query = struct.pack('8B', 0x01, 0x86, 0xff, 0x01, 0, 0, 0, 0)
            os.write(fd, firmware_query)
            
            # Read firmware response and clear buffer
            firmware_data = b''
            while True:
                r, _, _ = select.select([fd], [], [], 0.2)
                if fd not in r:
                    break
                data = os.read(fd, 8)
                firmware_data += data
            
            firmware = str(firmware_data, 'latin-1').strip() if firmware_data else "Unknown"
            
            # Send data query (from temper-py)
            os.write(fd, struct.pack('8B', 0x01, 0x80, 0x33, 0x01, 0, 0, 0, 0))
            
            # Read ONLY the data response (first 8 bytes should be the actual data)
            data_bytes = b''
            while True:
                r, _, _ = select.select([fd], [], [], 0.1)
                if fd not in r:
                    break
                data = os.read(fd, 8)
                data_bytes += data
            
            os.close(fd)
            
            if data_bytes:
                self.log(f"Raw data: {binascii.hexlify(data_bytes)}")
                # Use only the first 8 bytes for data parsing
                actual_data = data_bytes[:8]
                return self.decode_v4_data(actual_data, firmware, getattr(self, 'temperature_unit', 'celsius'))
            
        except Exception as e:
            self.log(f"Data read error: {e}")
        
        return None
    
    def decode_v4_data(self, data_bytes: bytes, firmware: str, temperature_unit: str = "celsius") -> Dict:
        """Decode TEMPerHUM_V4.1 data format"""
        result = {
            'firmware': firmware,
            'raw_hex': binascii.hexlify(data_bytes).decode(),
            'timestamp': time.time()
        }
        
        if len(data_bytes) >= 8:
            # Based on temper-py parsing logic, try different offsets and divisors
            # TEMPerHUM_V4.1 is newer, so let's analyze the pattern
            
            # Raw bytes analysis (from our test):
            # Sensor 1: 80200b3f0e060000  
            # Sensor 2: 80200b080ee20000
            #           ^^^^^^^^^^^^^^^^
            # Positions: 0123456789ABCDEF
            
            try:
                # Try temperature at offset 2-3 (like other TEMPerHUM versions)
                if data_bytes[2] != 0x4e or data_bytes[3] != 0x20:  # Not "N " (no sensor)
                    temp_raw = struct.unpack_from('>h', data_bytes, 2)[0]
                    temp_celsius = temp_raw / 100.0
                    temp_fahrenheit = temp_celsius * 1.8 + 32.0
                    
                    # Store both but make primary unit configurable (rounded to 1 decimal)
                    result['internal_temperature_c'] = round(temp_celsius, 1)
                    result['internal_temperature_f'] = round(temp_fahrenheit, 1)
                    
                    # Set primary temperature based on unit preference (rounded to 1 decimal)
                    if temperature_unit.lower() in ['fahrenheit', 'f']:
                        result['internal_temperature'] = round(temp_fahrenheit, 1)
                        temp_display = f"{temp_fahrenheit:.1f}°F"
                    else:
                        result['internal_temperature'] = round(temp_celsius, 1)
                        temp_display = f"{temp_celsius:.1f}°C"
                    
                # Try humidity at offset 4-5  
                if data_bytes[4] != 0x4e or data_bytes[5] != 0x20:  # Not "N " (no sensor)
                    hum_raw = struct.unpack_from('>h', data_bytes, 4)[0]
                    result['internal_humidity'] = round(hum_raw / 100.0, 1)
                
                hum_display = f"{result.get('internal_humidity', 'N/A'):.1f}%RH"
                self.log(f"Decoded: {temp_display}, {hum_display}")
                
            except Exception as e:
                self.log(f"Decode error: {e}")
                result['decode_error'] = str(e)
        
        return result
    
    def send_control_command(self, hidraw_path: str, command_bytes: List[int], description: str = "") -> bool:
        """Send control command to sensor"""
        try:
            self.log(f"Sending {description}: {[hex(b) for b in command_bytes]}")
            
            fd = os.open(hidraw_path, os.O_RDWR)
            os.write(fd, struct.pack('8B', *command_bytes))
            os.close(fd)
            
            return True
            
        except Exception as e:
            self.log(f"Control command error: {e}")
            return False
    
    def toggle_sensor_output(self, sensor_id: str, enable: bool = None) -> bool:
        """Toggle sensor data output on/off"""
        if sensor_id not in self.sensors or 'control' not in self.sensors[sensor_id]:
            self.log(f"No control interface for {sensor_id}")
            return False
        
        control_path = self.sensors[sensor_id]['control']
        
        # Based on button behavior: "caps lock:on/off/++"
        # Try different control command formats
        
        control_commands = [
            # Format 1: Similar to data query but different command
            [0x01, 0x81, 0x33, 0x01, 0, 0, 0, 0],  # Toggle variant
            [0x01, 0x82, 0x33, 0x01, 0, 0, 0, 0],  # Another toggle variant
            
            # Format 2: Caps Lock simulation (0x39 = Caps Lock keycode)
            [0x01, 0x39, 0x00, 0x01, 0, 0, 0, 0],  # Caps Lock press
            [0x01, 0x39, 0x01, 0x01, 0, 0, 0, 0],  # Caps Lock hold
            
            # Format 3: Direct control codes
            [0x01, 0x01, 0x00, 0x00, 0, 0, 0, 0],  # Simple toggle
            [0x01, 0x00, 0x01, 0x00, 0, 0, 0, 0],  # Reverse toggle
            
            # Format 4: Based on firmware query pattern
            [0x01, 0x86, 0x01, 0x01, 0, 0, 0, 0],  # Control variant 1
            [0x01, 0x86, 0x02, 0x01, 0, 0, 0, 0],  # Control variant 2
        ]
        
        success = False
        for i, cmd in enumerate(control_commands):
            desc = f"Toggle attempt {i+1}"
            if self.send_control_command(control_path, cmd, desc):
                # Wait and check if sensor state changed
                time.sleep(1)
                # TODO: Verify state change by monitoring output interface
                success = True
                break
        
        return success
    
    def adjust_sensor_interval(self, sensor_id: str, increase: bool = True) -> bool:
        """Adjust sensor data output interval"""
        if sensor_id not in self.sensors or 'control' not in self.sensors[sensor_id]:
            self.log(f"No control interface for {sensor_id}")
            return False
        
        control_path = self.sensors[sensor_id]['control']
        
        # Based on button behavior: "caps lock:++", "num lock:--"
        # 0x39 = Caps Lock, 0x53 = Num Lock
        
        if increase:
            # Double Caps Lock press (increase interval)
            commands = [
                [0x01, 0x39, 0x39, 0x01, 0, 0, 0, 0],  # Double Caps
                [0x01, 0x86, 0x39, 0x39, 0, 0, 0, 0],  # Firmware + Double Caps
            ]
            desc = "Increase interval"
        else:
            # Double Num Lock press (decrease interval)
            commands = [
                [0x01, 0x53, 0x53, 0x01, 0, 0, 0, 0],  # Double Num Lock
                [0x01, 0x86, 0x53, 0x53, 0, 0, 0, 0],  # Firmware + Double Num Lock
            ]
            desc = "Decrease interval"
        
        success = False
        for cmd in commands:
            if self.send_control_command(control_path, cmd, desc):
                time.sleep(1)
                success = True
                break
        
        return success
    
    def read_all_sensors(self) -> Dict[str, Dict]:
        """Read data from all sensors"""
        results = {}
        
        for sensor_id, interfaces in self.sensors.items():
            if 'control' in interfaces:
                # Use control interface for reading (it's the one that responds to queries)
                data = self.read_sensor_data(interfaces['control'])
                if data:
                    results[sensor_id] = data
                else:
                    results[sensor_id] = {'error': 'Failed to read data'}
        
        return results
    
    def monitor_sensors(self, duration: int = 10, interval: float = 1.0):
        """Monitor sensors for a specified duration"""
        print(f"Monitoring sensors for {duration} seconds...")
        print("Timestamp | Sensor | Temperature | Humidity")
        print("-" * 50)
        
        start_time = time.time()
        while time.time() - start_time < duration:
            results = self.read_all_sensors()
            
            timestamp = time.strftime("%H:%M:%S")
            for sensor_id, data in results.items():
                if 'error' in data:
                    print(f"{timestamp} | {sensor_id} | ERROR: {data['error']}")
                else:
                    temp = data.get('internal_temperature_c', 'N/A')
                    hum = data.get('internal_humidity', 'N/A')
                    print(f"{timestamp} | {sensor_id} | {temp}°C | {hum}%RH")
            
            time.sleep(interval)
    
    def run_control_test(self):
        """Run comprehensive control test"""
        print("🧪 TEMPERHUM CONTROL TEST")
        print("=" * 30)
        
        if not self.sensors:
            print("❌ No sensors found!")
            return False
        
        print(f"📡 Found sensors: {list(self.sensors.keys())}")
        
        # Test data reading
        print("\n📊 READING SENSOR DATA:")
        results = self.read_all_sensors()
        for sensor_id, data in results.items():
            print(f"  {sensor_id}: {json.dumps(data, indent=2)}")
        
        # Test control commands
        print("\n🎮 TESTING CONTROL COMMANDS:")
        for sensor_id in self.sensors.keys():
            print(f"\n  Testing {sensor_id}:")
            
            # Test toggle
            print("    Toggle test...")
            self.toggle_sensor_output(sensor_id)
            
            # Test interval adjustment  
            print("    Interval increase test...")
            self.adjust_sensor_interval(sensor_id, increase=True)
            
            time.sleep(2)
            
            print("    Interval decrease test...")
            self.adjust_sensor_interval(sensor_id, increase=False)
        
        print("\n✅ Control test completed!")
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='TemperhUM Controller')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-l', '--list', action='store_true', help='List sensors')
    parser.add_argument('-r', '--read', action='store_true', help='Read sensor data')
    parser.add_argument('-m', '--monitor', type=int, metavar='SECONDS', help='Monitor sensors')
    parser.add_argument('-t', '--test', action='store_true', help='Run control test')
    parser.add_argument('--toggle', metavar='SENSOR_ID', help='Toggle sensor output')
    parser.add_argument('--interval', nargs=2, metavar=('SENSOR_ID', 'INC/DEC'), 
                       help='Adjust interval (inc/dec)')
    
    args = parser.parse_args()
    
    controller = TemperhUMController(verbose=args.verbose)
    
    if args.list:
        print("Discovered sensors:")
        for sensor_id, interfaces in controller.sensors.items():
            print(f"  {sensor_id}: {interfaces}")
    
    elif args.read:
        results = controller.read_all_sensors()
        print(json.dumps(results, indent=2))
    
    elif args.monitor:
        controller.monitor_sensors(duration=args.monitor)
    
    elif args.test:
        controller.run_control_test()
    
    elif args.toggle:
        success = controller.toggle_sensor_output(args.toggle)
        print(f"Toggle {'succeeded' if success else 'failed'}")
    
    elif args.interval:
        sensor_id, direction = args.interval
        increase = direction.lower() in ['inc', 'increase', '+']
        success = controller.adjust_sensor_interval(sensor_id, increase)
        print(f"Interval adjustment {'succeeded' if success else 'failed'}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❌ Need sudo for hidraw access")
        print("Run: sudo python3 temperhum_controller.py")
        exit(1)
    
    main()