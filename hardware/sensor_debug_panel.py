#!/usr/bin/env python3
"""
TEMPerHUM Sensor Debug Panel
============================

Real-time debug panel showing status of both TEMPerHUM sensors.
Detects activation/deactivation and displays current readings.

Usage:
    python3 sensor_debug_panel.py
"""

import os
import sys
import time
import json
import subprocess
import re
import threading
from datetime import datetime
import curses
import signal

class SensorDebugPanel:
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
                    
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            self.running = False
    
    def draw_panel(self, stdscr):
        """Draw the debug panel."""
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()
        
        # Get screen dimensions
        height, width = stdscr.getmaxyx()
        
        # Title
        title = "🐢 TEMPerHUM Sensor Debug Panel"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Instructions
        instructions = "Press TXT buttons on sensors or hold Num Lock for 3 seconds | Press 'q' to quit"
        stdscr.addstr(1, 0, instructions[:width-1], curses.A_DIM)
        
        # Separator
        stdscr.addstr(2, 0, "=" * width)
        
        # Sensor status panels
        panel_width = (width - 3) // 2
        panel_height = height - 8
        
        # Sensor 1 Panel
        self.draw_sensor_panel(stdscr, 3, 1, 'sensor_1', panel_width, panel_height)
        
        # Sensor 2 Panel
        self.draw_sensor_panel(stdscr, 3, panel_width + 2, 'sensor_2', panel_width, panel_height)
        
        # Activity log
        log_y = 3 + panel_height + 1
        if log_y < height - 2:
            stdscr.addstr(log_y, 0, "📋 Recent Activity:", curses.A_BOLD)
            stdscr.addstr(log_y + 1, 0, "-" * width)
            
            # Show recent captured data
            recent_data = self.captured_data[-10:]  # Last 10 entries
            for i, data in enumerate(recent_data):
                if log_y + 2 + i < height - 1:
                    timestamp = data['timestamp'].split('T')[1][:8]  # HH:MM:SS
                    line = f"{timestamp}: {data['raw_data'][:width-15]}"
                    stdscr.addstr(log_y + 2 + i, 0, line[:width-1])
        
        # Status bar
        status_line = f"Last Activity: {self.last_activity.strftime('%H:%M:%S') if self.last_activity else 'None'} | Total Captured: {len(self.captured_data)} | Press 'q' to quit"
        stdscr.addstr(height - 1, 0, status_line[:width-1], curses.A_REVERSE)
        
        stdscr.refresh()
    
    def draw_sensor_panel(self, stdscr, start_y, start_x, sensor_id, width, height):
        """Draw individual sensor panel."""
        sensor = self.sensors[sensor_id]
        
        # Panel border
        for y in range(start_y, start_y + height):
            if y < stdscr.getmaxyx()[0]:
                stdscr.addch(y, start_x, '|')
                stdscr.addch(y, start_x + width - 1, '|')
        
        for x in range(start_x, start_x + width):
            if start_y < stdscr.getmaxyx()[0]:
                stdscr.addch(start_y, x, '-')
            if start_y + height - 1 < stdscr.getmaxyx()[0]:
                stdscr.addch(start_y + height - 1, x, '-')
        
        # Sensor name
        name = sensor['name']
        stdscr.addstr(start_y + 1, start_x + 2, name, curses.A_BOLD)
        
        # Status indicator
        status_y = start_y + 3
        if sensor['status'] == 'active':
            status = "🟢 ACTIVE"
            status_attr = curses.A_BOLD | curses.color_pair(2) if curses.has_colors() else curses.A_BOLD
        else:
            status = "🔴 INACTIVE"
            status_attr = curses.A_BOLD | curses.color_pair(1) if curses.has_colors() else curses.A_BOLD
        
        stdscr.addstr(status_y, start_x + 2, status, status_attr)
        
        # Current readings
        readings_y = start_y + 5
        if sensor['temperature'] is not None and sensor['humidity'] is not None:
            temp_str = f"Temperature: {sensor['temperature']:.1f}°C"
            hum_str = f"Humidity: {sensor['humidity']:.1f}%"
            
            stdscr.addstr(readings_y, start_x + 2, temp_str)
            stdscr.addstr(readings_y + 1, start_x + 2, hum_str)
        else:
            stdscr.addstr(readings_y, start_x + 2, "No readings available")
        
        # Last update
        update_y = start_y + 8
        if sensor['last_update']:
            update_str = f"Last Update: {sensor['last_update'].strftime('%H:%M:%S')}"
            stdscr.addstr(update_y, start_x + 2, update_str)
        
        # Readings count
        count_y = start_y + 9
        count_str = f"Readings: {sensor['readings_count']}"
        stdscr.addstr(count_y, start_x + 2, count_str)
        
        # Last raw data
        if sensor['last_reading']:
            data_y = start_y + 11
            data_str = f"Last: {sensor['last_reading'][:width-8]}"
            stdscr.addstr(data_y, start_x + 2, data_str, curses.A_DIM)
    
    def run_panel(self):
        """Run the debug panel."""
        # Start input capture in background thread
        capture_thread = threading.Thread(target=self.capture_input, daemon=True)
        capture_thread.start()
        
        # Initialize curses
        try:
            stdscr = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_RED, -1)    # Red for inactive
            curses.init_pair(2, curses.COLOR_GREEN, -1)  # Green for active
            
            # Handle window resize
            def resize_handler(signum, frame):
                curses.endwin()
                curses.initscr()
                curses.start_color()
                curses.use_default_colors()
                curses.init_pair(1, curses.COLOR_RED, -1)
                curses.init_pair(2, curses.COLOR_GREEN, -1)
            
            signal.signal(signal.SIGWINCH, resize_handler)
            
            # Main loop
            while self.running:
                try:
                    # Check for quit key
                    stdscr.timeout(100)  # 100ms timeout
                    key = stdscr.getch()
                    if key == ord('q') or key == ord('Q'):
                        break
                    
                    # Draw panel
                    self.draw_panel(stdscr)
                    
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"Panel error: {e}")
        finally:
            curses.endwin()
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
                'session_duration': None  # Could calculate if we track start time
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
    print("Press 'q' to quit the panel")
    print("")
    
    # Create and run debug panel
    panel = SensorDebugPanel()
    
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