#!/usr/bin/env python3
"""
Simple TEMPerHUM Sensor Debug Panel
===================================

Real-time debug panel showing status of both TEMPerHUM sensors.
Uses simple terminal output with periodic updates.

Usage:
    python3 simple_debug_panel.py
"""

import os
import sys
import time
import json
import subprocess
import re
import threading
from datetime import datetime

class SimpleDebugPanel:
    def __init__(self):
        self.sensors = {
            'sensor_1': {
                'name': 'Sensor 1 (Inner)',
                'status': 'inactive',
                'last_reading': None,
                'last_update': None,
                'readings_count': 0,
                'temperature': None,
                'humidity': None
            },
            'sensor_2': {
                'name': 'Sensor 2 (Outer)',
                'status': 'inactive',
                'last_reading': None,
                'last_update': None,
                'readings_count': 0,
                'temperature': None,
                'humidity': None
            }
        }
        self.running = True
        self.captured_data = []
        self.last_activity = None
        self.start_time = datetime.now()
        
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
    
    def identify_sensor(self, raw_data):
        """Identify which sensor the data comes from."""
        # Sensor 1 typically shows banner text
        if any(keyword in raw_data.lower() for keyword in ['type:inner', 'inner-temp', 'inner-hum']):
            return 'sensor_1'
        # Sensor 2 shows actual data
        elif self.parse_temperhum_data(raw_data):
            return 'sensor_2'
        else:
            return 'unknown'
    
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
    
    def capture_input(self):
        """Capture input from sensors in a separate thread."""
        print("🔍 Starting sensor monitoring...")
        print("Press TXT buttons on sensors or hold Num Lock for 3 seconds")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                try:
                    line = input().strip()
                    if not line:
                        continue
                    
                    # Store captured data
                    data_point = {
                        'timestamp': datetime.now().isoformat(),
                        'raw_data': line
                    }
                    self.captured_data.append(data_point)
                    
                    # Parse data
                    parsed = self.parse_temperhum_data(line)
                    if parsed:
                        data_point['parsed'] = parsed
                    
                    # Identify sensor
                    sensor_id = self.identify_sensor(line)
                    
                    # Update sensor status
                    self.update_sensor_status(sensor_id, line, parsed)
                    
                    # Show immediate feedback
                    if sensor_id != 'unknown':
                        sensor = self.sensors[sensor_id]
                        if parsed:
                            print(f"✅ {sensor['name']}: {parsed['temperature']:.1f}°C, {parsed['humidity']:.1f}%")
                        else:
                            print(f"📝 {sensor['name']}: {line}")
                    
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            self.running = False
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def draw_panel(self):
        """Draw the debug panel."""
        self.clear_screen()
        
        # Title
        print("🐢 TEMPerHUM Sensor Debug Panel")
        print("=" * 50)
        
        # Instructions
        print("Press TXT buttons on sensors or hold Num Lock for 3 seconds | Press Ctrl+C to quit")
        print()
        
        # Sensor status panels
        print("SENSOR STATUS:")
        print("-" * 50)
        
        for sensor_id, sensor in self.sensors.items():
            # Sensor name and status
            status_icon = "🟢" if sensor['status'] == 'active' else "🔴"
            print(f"{status_icon} {sensor['name']}: {sensor['status'].upper()}")
            
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
        print("-" * 50)
        session_duration = datetime.now() - self.start_time
        print(f"Session Duration: {session_duration}")
        print(f"Total Captured: {len(self.captured_data)} lines")
        print(f"Last Activity: {self.last_activity.strftime('%H:%M:%S') if self.last_activity else 'None'}")
        print()
        
        # Recent activity
        if self.captured_data:
            print("RECENT ACTIVITY (last 5):")
            print("-" * 50)
            recent_data = self.captured_data[-5:]
            for data in recent_data:
                timestamp = data['timestamp'].split('T')[1][:8]  # HH:MM:SS
                print(f"{timestamp}: {data['raw_data']}")
            print()
    
    def run_panel(self):
        """Run the debug panel."""
        # Start input capture in background thread
        capture_thread = threading.Thread(target=self.capture_input, daemon=True)
        capture_thread.start()
        
        # Give capture thread time to start
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
        filename = f"debug_session_{timestamp}.json"
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'sensors': self.sensors,
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
    print("🐢 TEMPerHUM Sensor Debug Panel")
    print("=" * 50)
    
    # Check for sensors
    result = subprocess.run("lsusb | grep -i temperhum", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ TEMPerHUM sensors detected:")
        print(result.stdout.strip())
    else:
        print("⚠️ No TEMPerHUM sensors detected")
        print("Make sure sensors are plugged in")
    
    print("\n🚀 Starting debug panel...")
    print("Press Ctrl+C to stop")
    print("")
    
    # Create and run debug panel
    panel = SimpleDebugPanel()
    
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
        print("=" * 30)
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