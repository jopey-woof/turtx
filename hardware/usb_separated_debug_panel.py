#!/usr/bin/env python3
"""
USB-Separated TEMPerHUM Sensor Debug Panel
==========================================

Real-time debug panel that distinguishes between two TEMPerHUM sensors
by their USB device paths and captures output to separate files.

Usage:
    python3 usb_separated_debug_panel.py
"""

import os
import sys
import time
import json
import subprocess
import re
import threading
from datetime import datetime

class USBSeparatedDebugPanel:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1 (Inner)',
                'usb_path': None,
                'status': 'inactive',
                'last_reading': None,
                'last_update': None,
                'readings_count': 0,
                'temperature': None,
                'humidity': None,
                'capture_file': None
            },
            'sensor_2': {
                'name': 'Sensor 2 (Outer)',
                'usb_path': None,
                'status': 'inactive',
                'last_reading': None,
                'last_update': None,
                'readings_count': 0,
                'temperature': None,
                'humidity': None,
                'capture_file': None
            }
        }
        self.running = True
        self.captured_data = []
        self.last_activity = None
        self.start_time = datetime.now()
        
    def find_temperhum_devices(self):
        """Find TEMPerHUM devices and their USB paths."""
        print("🔍 Finding TEMPerHUM devices...")
        
        # Get USB device list
        result = subprocess.run("lsusb", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return []
        
        temperhum_devices = []
        for line in result.stdout.split('\n'):
            if "3553:a001" in line and "TEMPerHUM" in line:
                # Extract bus and device numbers
                match = re.search(r'Bus (\d+) Device (\d+):', line)
                if match:
                    bus = match.group(1)
                    device = match.group(2)
                    usb_path = f"/dev/bus/usb/{bus.zfill(3)}/{device.zfill(3)}"
                    temperhum_devices.append({
                        'line': line.strip(),
                        'bus': bus,
                        'device': device,
                        'usb_path': usb_path
                    })
                    print(f"✅ Found: {line.strip()}")
                    print(f"   USB Path: {usb_path}")
        
        return temperhum_devices
    
    def assign_sensors_to_usb_ports(self):
        """Assign sensors to USB ports based on device order."""
        devices = self.find_temperhum_devices()
        
        if len(devices) >= 2:
            # Assign first device to sensor 1, second to sensor 2
            self.sensors['sensor_1']['usb_path'] = devices[0]['usb_path']
            self.sensors['sensor_2']['usb_path'] = devices[1]['usb_path']
            
            print(f"\n📋 Sensor Assignment:")
            print(f"  Sensor 1 (Inner): {devices[0]['usb_path']}")
            print(f"  Sensor 2 (Outer): {devices[1]['usb_path']}")
            return True
        elif len(devices) == 1:
            print(f"⚠️ Only 1 sensor found: {devices[0]['usb_path']}")
            self.sensors['sensor_1']['usb_path'] = devices[0]['usb_path']
            return False
        else:
            print("❌ No TEMPerHUM sensors found")
            return False
    
    def create_capture_files(self):
        """Create separate capture files for each sensor."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for sensor_id, sensor in self.sensors.items():
            if sensor['usb_path']:
                # Create capture file based on USB path
                bus_device = sensor['usb_path'].split('/')[-2] + '_' + sensor['usb_path'].split('/')[-1]
                sensor['capture_file'] = f"/tmp/temperhum_{sensor_id}_{bus_device}_{timestamp}.txt"
                
                # Create capture script for this sensor
                self.create_sensor_capture_script(sensor_id, sensor)
        
        print(f"\n📁 Capture files created:")
        for sensor_id, sensor in self.sensors.items():
            if sensor['capture_file']:
                print(f"  {sensor['name']}: {sensor['capture_file']}")
    
    def create_sensor_capture_script(self, sensor_id, sensor):
        """Create a capture script for a specific sensor."""
        script_content = f'''#!/usr/bin/env python3
"""
Capture script for {sensor['name']}
USB Path: {sensor['usb_path']}
Output File: {sensor['capture_file']}
"""

import sys
from datetime import datetime

output_file = "{sensor['capture_file']}"

print(f"🐢 Starting capture for {sensor['name']}")
print(f"📁 Output: {{output_file}}")
print("Press TXT button on this sensor or hold Num Lock for 3 seconds")
print("Press Ctrl+C to stop")

try:
    with open(output_file, 'w') as f:
        f.write(f"Capture started at {{datetime.now()}}\\n")
        f.write(f"Sensor: {sensor['name']}\\n")
        f.write(f"USB Path: {sensor['usb_path']}\\n")
        f.write("=" * 50 + "\\n")
        
        line_count = 0
        while True:
            try:
                line = input().strip()
                line_count += 1
                
                # Write to file with timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%3N')
                f.write(f"{{timestamp}}: {{line}}\\n")
                f.flush()  # Ensure data is written immediately
                
                # Show progress
                print(f"📥 {{line_count}}: {{line}}")
                
            except EOFError:
                break
                
except KeyboardInterrupt:
    print("\\n⏹️ Capture stopped by user")
    print(f"📁 Data saved to: {{output_file}}")
    print(f"📊 Total lines captured: {{line_count}}")
'''
        
        script_path = f"/tmp/capture_{sensor_id}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        sensor['capture_script'] = script_path
    
    def parse_temperhum_data(self, raw_data):
        """Parse TEMPerHUM data in the exact format we discovered."""
        patterns = [
            r'(\d+\.?\d*)\s*\[C\]\s*(\d+\.?\d*)\s*\[%RH\]\s*(\d+)S',
            r'(\d+\.?\d*)\[C\](\d+\.?\d*)\[%RH\](\d+)S',
            r'(\d+\.?\d*)\s+\[C\]\s+(\d+\.?\d*)\s+\[%RH\]\s+(\d+)S',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, raw_data, re.IGNORECASE)
            if match:
                try:
                    temperature = float(match.group(1))
                    humidity = float(match.group(2))
                    interval = int(match.group(3))
                    
                    return {
                        'temperature': temperature,
                        'humidity': humidity,
                        'interval': interval,
                        'raw_data': raw_data
                    }
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def monitor_capture_files(self):
        """Monitor capture files for new data."""
        print("🔍 Monitoring capture files...")
        
        # Track file positions for each sensor
        file_positions = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor['capture_file']:
                file_positions[sensor_id] = 0
        
        while self.running:
            for sensor_id, sensor in self.sensors.items():
                if not sensor['capture_file'] or not os.path.exists(sensor['capture_file']):
                    continue
                
                try:
                    with open(sensor['capture_file'], 'r') as f:
                        # Read from last position
                        f.seek(file_positions[sensor_id])
                        new_lines = f.readlines()
                        file_positions[sensor_id] = f.tell()
                        
                        # Process new lines
                        for line in new_lines:
                            line = line.strip()
                            if not line or line.startswith('='):
                                continue
                            
                            # Parse timestamp and data
                            if ': ' in line:
                                timestamp_str, data = line.split(': ', 1)
                                try:
                                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                                except:
                                    timestamp = datetime.now()
                            else:
                                data = line
                                timestamp = datetime.now()
                            
                            # Store captured data
                            data_point = {
                                'timestamp': timestamp.isoformat(),
                                'sensor_id': sensor_id,
                                'raw_data': data
                            }
                            self.captured_data.append(data_point)
                            
                            # Parse data
                            parsed = self.parse_temperhum_data(data)
                            if parsed:
                                data_point['parsed'] = parsed
                                self.update_sensor_status(sensor_id, data, parsed)
                                print(f"✅ {sensor['name']}: {parsed['temperature']:.1f}°C, {parsed['humidity']:.1f}%")
                            else:
                                self.update_sensor_status(sensor_id, data, None)
                                print(f"📝 {sensor['name']}: {data}")
                            
                except Exception as e:
                    print(f"Error reading {sensor['capture_file']}: {e}")
            
            time.sleep(0.5)  # Check every 500ms
    
    def update_sensor_status(self, sensor_id, raw_data, parsed_data=None):
        """Update sensor status and readings."""
        now = datetime.now()
        
        if sensor_id in self.sensors:
            sensor = self.sensors[sensor_id]
            
            # Update status
            if parsed_data:
                sensor['status'] = 'active'
                sensor['temperature'] = parsed_data['temperature']
                sensor['humidity'] = parsed_data['humidity']
                sensor['readings_count'] += 1
            else:
                # Banner text or other output
                sensor['status'] = 'active'
                sensor['temperature'] = None
                sensor['humidity'] = None
            
            sensor['last_reading'] = raw_data
            sensor['last_update'] = now
            self.last_activity = now
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def draw_panel(self):
        """Draw the debug panel."""
        self.clear_screen()
        
        # Title
        print("🐢 USB-Separated TEMPerHUM Sensor Debug Panel")
        print("=" * 60)
        
        # Instructions
        print("Run capture scripts in separate terminals, then activate sensors")
        print("Press Ctrl+C to quit")
        print()
        
        # Sensor status panels
        print("SENSOR STATUS:")
        print("-" * 60)
        
        for sensor_id, sensor in self.sensors.items():
            # Sensor name and status
            status_icon = "🟢" if sensor['status'] == 'active' else "🔴"
            print(f"{status_icon} {sensor['name']}: {sensor['status'].upper()}")
            
            # USB path
            if sensor['usb_path']:
                print(f"   USB Path: {sensor['usb_path']}")
            
            # Capture file
            if sensor['capture_file']:
                print(f"   Capture File: {os.path.basename(sensor['capture_file'])}")
            
            # Current readings
            if sensor['temperature'] is not None and sensor['humidity'] is not None:
                print(f"   Temperature: {sensor['temperature']:.1f}°C")
                print(f"   Humidity: {sensor['humidity']:.1f}%")
            else:
                print("   No readings available")
            
            # Last update
            if sensor['last_update']:
                print(f"   Last Update: {sensor['last_update'].strftime('%H:%M:%S')}")
            
            # Readings count
            print(f"   Readings: {sensor['readings_count']}")
            
            # Last raw data
            if sensor['last_reading']:
                print(f"   Last Data: {sensor['last_reading']}")
            
            print()
        
        # Activity summary
        print("ACTIVITY SUMMARY:")
        print("-" * 60)
        session_duration = datetime.now() - self.start_time
        print(f"Session Duration: {session_duration}")
        print(f"Total Captured: {len(self.captured_data)} lines")
        print(f"Last Activity: {self.last_activity.strftime('%H:%M:%S') if self.last_activity else 'None'}")
        print()
        
        # Recent activity
        if self.captured_data:
            print("RECENT ACTIVITY (last 5):")
            print("-" * 60)
            recent_data = self.captured_data[-5:]
            for data in recent_data:
                timestamp = data['timestamp'].split('T')[1][:8]  # HH:MM:SS
                sensor_name = self.sensors[data['sensor_id']]['name'] if 'sensor_id' in data else 'Unknown'
                print(f"{timestamp} [{sensor_name}]: {data['raw_data']}")
            print()
        
        # Capture instructions
        print("CAPTURE INSTRUCTIONS:")
        print("-" * 60)
        for sensor_id, sensor in self.sensors.items():
            if sensor['capture_script']:
                print(f"Terminal {sensor_id[-1]}: python3 {sensor['capture_script']}")
        print()
    
    def run_panel(self):
        """Run the debug panel."""
        # Assign sensors to USB ports
        if not self.assign_sensors_to_usb_ports():
            print("❌ Cannot proceed without sensors")
            return
        
        # Create capture files and scripts
        self.create_capture_files()
        
        # Start file monitoring in background thread
        monitor_thread = threading.Thread(target=self.monitor_capture_files, daemon=True)
        monitor_thread.start()
        
        # Give monitor thread time to start
        time.sleep(1)
        
        # Main loop
        try:
            while self.running:
                # Draw panel
                self.draw_panel()
                
                # Wait before next update
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.running = False
    
    def save_session(self):
        """Save debug session data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"usb_debug_session_{timestamp}.json"
        
        # Convert datetime objects to strings for JSON serialization
        sensors_for_json = {}
        for sensor_id, sensor in self.sensors.items():
            sensors_for_json[sensor_id] = sensor.copy()
            if sensor['last_update']:
                sensors_for_json[sensor_id]['last_update'] = sensor['last_update'].isoformat()
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'sensors': sensors_for_json,
            'captured_data': self.captured_data,
            'summary': {
                'total_captured': len(self.captured_data),
                'sensor_1_readings': self.sensors['sensor_1']['readings_count'],
                'sensor_2_readings': self.sensors['sensor_2']['readings_count'],
                'session_duration': str(datetime.now() - self.start_time)
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return filename

def main():
    """Main function."""
    print("🐢 USB-Separated TEMPerHUM Sensor Debug Panel")
    print("=" * 60)
    
    # Create and run debug panel
    panel = USBSeparatedDebugPanel()
    
    try:
        panel.run_panel()
    except KeyboardInterrupt:
        print("\n⏹️ Debug panel stopped by user")
    finally:
        # Save session data
        if panel.captured_data:
            filename = panel.save_session()
            print(f"\n📁 Session data saved to: {filename}")
        
        # Display final summary
        print("\n📊 FINAL SESSION SUMMARY:")
        print("=" * 40)
        for sensor_id, sensor in panel.sensors.items():
            print(f"{sensor['name']}:")
            print(f"  Status: {sensor['status']}")
            print(f"  Readings: {sensor['readings_count']}")
            if sensor['temperature'] and sensor['humidity']:
                print(f"  Last: {sensor['temperature']:.1f}°C, {sensor['humidity']:.1f}%")
            print()
        
        print(f"Total captured: {len(panel.captured_data)} lines")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1) 