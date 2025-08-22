#!/usr/bin/env python3
"""
File-Based TEMPerHUM Sensor Capture
==================================

Captures TEMPerHUM sensor output to files instead of terminal to avoid interference.
Uses multiple methods to capture keyboard input streams.

Usage:
    python3 file_capture_sensors.py
"""

import os
import sys
import time
import json
import subprocess
import re
import threading
from datetime import datetime

def run_cmd(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def find_temperhum_devices():
    """Find TEMPerHUM devices."""
    print("🔍 Finding TEMPerHUM devices...")
    
    output, code = run_cmd("lsusb")
    if code != 0:
        return []
    
    devices = []
    for line in output.split('\n'):
        if "3553:a001" in line and "TEMPerHUM" in line:
            devices.append(line.strip())
            print(f"✅ TEMPerHUM found: {line.strip()}")
    
    return devices

def capture_to_file_method1():
    """Method 1: Use script to capture input to file."""
    print("📁 Method 1: Direct file capture")
    
    # Create a simple capture script
    capture_script = '''#!/bin/bash
# Capture sensor output to file
OUTPUT_FILE="/tmp/temperhum_capture_$(date +%Y%m%d_%H%M%S).txt"
echo "Starting capture to $OUTPUT_FILE..."
echo "Press TXT buttons on sensors or hold Num Lock for 3 seconds"
echo "Press Ctrl+C to stop"

# Capture all input to file
cat > "$OUTPUT_FILE" 2>&1
'''
    
    script_path = "/tmp/capture_sensors.sh"
    with open(script_path, 'w') as f:
        f.write(capture_script)
    
    os.chmod(script_path, 0o755)
    
    print(f"✅ Capture script created: {script_path}")
    print("Run this script in a separate terminal:")
    print(f"  {script_path}")
    
    return script_path

def capture_to_file_method2():
    """Method 2: Use tee to capture to file while showing output."""
    print("📁 Method 2: Tee capture (shows output and saves to file)")
    
    output_file = f"/tmp/temperhum_tee_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    capture_cmd = f"tee {output_file}"
    
    print(f"✅ Tee command ready: {capture_cmd}")
    print("Run this command in a separate terminal:")
    print(f"  {capture_cmd}")
    print("Then activate sensors and watch the output")
    
    return output_file

def capture_to_file_method3():
    """Method 3: Use script with background monitoring."""
    print("📁 Method 3: Background monitoring script")
    
    monitor_script = '''#!/bin/bash
# Background monitoring of sensor output
OUTPUT_FILE="/tmp/temperhum_monitor_$(date +%Y%m%d_%H%M%S).txt"
LOG_FILE="/tmp/temperhum_monitor.log"

echo "Starting background monitoring..."
echo "Output file: $OUTPUT_FILE"
echo "Log file: $LOG_FILE"

# Function to capture input
capture_input() {
    echo "Monitoring started at $(date)" > "$LOG_FILE"
    echo "Press TXT buttons on sensors or hold Num Lock for 3 seconds"
    
    # Use a simple loop to capture input
    while true; do
        if read -t 1 line; then
            echo "$(date '+%Y-%m-%d %H:%M:%S.%3N'): $line" >> "$OUTPUT_FILE"
            echo "Captured: $line"
        fi
    done
}

# Start capture in background
capture_input &
CAPTURE_PID=$!

echo "Capture started with PID: $CAPTURE_PID"
echo "Press Enter to stop monitoring..."

read
kill $CAPTURE_PID
echo "Monitoring stopped. Check $OUTPUT_FILE for captured data."
'''
    
    script_path = "/tmp/monitor_sensors.sh"
    with open(script_path, 'w') as f:
        f.write(monitor_script)
    
    os.chmod(script_path, 0o755)
    
    print(f"✅ Monitor script created: {script_path}")
    print("Run this script in a separate terminal:")
    print(f"  {script_path}")
    
    return script_path

def capture_to_file_method4():
    """Method 4: Use Python script to capture to file."""
    print("📁 Method 4: Python file capture")
    
    python_capture_script = '''#!/usr/bin/env python3
import sys
import time
from datetime import datetime

output_file = f"/tmp/temperhum_python_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

print(f"Starting Python capture to {output_file}")
print("Press TXT buttons on sensors or hold Num Lock for 3 seconds")
print("Press Ctrl+C to stop")

try:
    with open(output_file, 'w') as f:
        f.write(f"Capture started at {datetime.now()}\\n")
        
        while True:
            try:
                line = input()
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%3N')
                f.write(f"{timestamp}: {line}\\n")
                f.flush()  # Ensure data is written immediately
                print(f"Captured: {line}")
            except EOFError:
                break
except KeyboardInterrupt:
    print("\\nCapture stopped by user")
    print(f"Data saved to: {output_file}")
'''
    
    script_path = "/tmp/python_capture.py"
    with open(script_path, 'w') as f:
        f.write(python_capture_script)
    
    os.chmod(script_path, 0o755)
    
    print(f"✅ Python capture script created: {script_path}")
    print("Run this script in a separate terminal:")
    print(f"  python3 {script_path}")
    
    return script_path

def parse_captured_file(file_path):
    """Parse captured data from file."""
    print(f"🔍 Parsing captured data from: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return []
    
    parsed_data = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            # Skip timestamp prefixes if present
            if ': ' in line:
                line = line.split(': ', 1)[1]
            
            # Parse TEMPerHUM data
            parsed = parse_temperhum_data(line)
            if parsed:
                parsed_data.append({
                    'line_number': line_num,
                    'raw_data': line,
                    'parsed': parsed,
                    'timestamp': datetime.now().isoformat()
                })
    
    return parsed_data

def parse_temperhum_data(raw_data):
    """Parse TEMPerHUM data in the exact format we discovered."""
    # Format: 28.24 [C] 36.97 [%RH] 1S (with tabs and spaces)
    patterns = [
        # Standard format with tabs
        r'(\d+\.?\d*)\s*\[C\]\s*(\d+\.?\d*)\s*\[%RH\]\s*(\d+)S',
        # Compact format
        r'(\d+\.?\d*)\[C\](\d+\.?\d*)\[%RH\](\d+)S',
        # Space-separated format
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

def create_remote_capture_script():
    """Create a comprehensive remote capture script."""
    remote_script = '''#!/usr/bin/env python3
"""
Remote TEMPerHUM File Capture
============================

Captures sensor output to files on remote machine.
Run this on the remote machine when sensors are plugged in.
"""

import os
import sys
import time
import json
import subprocess
import re
from datetime import datetime

def parse_temperhum_data(raw_data):
    """Parse TEMPerHUM data."""
    patterns = [
        r'(\\d+\\.?\\d*)\\s*\\[C\\]\\s*(\\d+\\.?\\d*)\\s*\\[%RH\\]\\s*(\\d+)S',
        r'(\\d+\\.?\\d*)\\[C\\](\\d+\\.?\\d*)\\[%RH\\](\\d+)S',
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

def capture_sensors_to_file():
    """Capture sensor data to file."""
    print("🐢 Remote TEMPerHUM File Capture")
    print("=" * 40)
    
    # Check for sensors
    result = subprocess.run("lsusb | grep -i temperhum", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ TEMPerHUM sensors detected")
        print(result.stdout.strip())
    else:
        print("⚠️ No TEMPerHUM sensors detected")
        print("Make sure sensors are plugged in")
    
    # Create output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/tmp/temperhum_remote_{timestamp}.txt"
    
    print(f"\\n📁 Capturing to: {output_file}")
    print("Instructions:")
    print("1. Press TXT button on sensors or hold Num Lock for 3 seconds")
    print("2. Watch for data being captured")
    print("3. Type 'quit' to stop")
    print("")
    
    captured_data = []
    
    try:
        with open(output_file, 'w') as f:
            f.write(f"Capture started at {datetime.now()}\\n")
            f.write("=" * 50 + "\\n")
            
            while True:
                try:
                    line = input().strip()
                    
                    if line.lower() == 'quit':
                        break
                    
                    # Write to file
                    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%3N')
                    f.write(f"{timestamp_str}: {line}\\n")
                    f.flush()
                    
                    # Parse data
                    parsed = parse_temperhum_data(line)
                    if parsed:
                        data_point = {
                            'timestamp': datetime.now().isoformat(),
                            'temperature': parsed['temperature'],
                            'humidity': parsed['humidity'],
                            'interval': parsed['interval'],
                            'raw_data': line
                        }
                        captured_data.append(data_point)
                        print(f"✅ {parsed['temperature']}°C, {parsed['humidity']}%")
                    else:
                        print(f"📝 Raw: {line}")
                        
                except EOFError:
                    break
                    
    except KeyboardInterrupt:
        print("\\n⏹️ Capture stopped by user")
    
    # Save parsed data to JSON
    if captured_data:
        json_file = f"/tmp/temperhum_remote_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(captured_data, f, indent=2)
        
        print(f"\\n📁 Raw data saved to: {output_file}")
        print(f"📁 Parsed data saved to: {json_file}")
        
        # Display summary
        temps = [d['temperature'] for d in captured_data]
        hums = [d['humidity'] for d in captured_data]
        print(f"📊 Summary: {len(captured_data)} readings")
        print(f"  Temperature: {min(temps):.1f}-{max(temps):.1f}°C")
        print(f"  Humidity: {min(hums):.1f}-{max(hums):.1f}%")
    else:
        print("❌ No data captured")

if __name__ == "__main__":
    capture_sensors_to_file()
'''
    
    script_path = "/tmp/remote_file_capture.py"
    with open(script_path, 'w') as f:
        f.write(remote_script)
    
    os.chmod(script_path, 0o755)
    
    print(f"✅ Remote capture script created: {script_path}")
    return script_path

def main():
    """Main function."""
    print("🐢 File-Based TEMPerHUM Sensor Capture")
    print("=" * 50)
    
    # Check for sensors
    devices = find_temperhum_devices()
    if len(devices) < 2:
        print("⚠️ Warning: Less than 2 sensors detected")
    
    print(f"\n📁 Creating file capture methods...")
    
    # Create different capture methods
    method1_script = capture_to_file_method1()
    method2_file = capture_to_file_method2()
    method3_script = capture_to_file_method3()
    method4_script = capture_to_file_method4()
    remote_script = create_remote_capture_script()
    
    print(f"\n" + "=" * 50)
    print("📋 FILE CAPTURE METHODS CREATED")
    print("=" * 50)
    
    print(f"1. Direct capture: {method1_script}")
    print(f"2. Tee capture: {method2_file}")
    print(f"3. Background monitor: {method3_script}")
    print(f"4. Python capture: {method4_script}")
    print(f"5. Remote capture: {remote_script}")
    
    print(f"\n💡 USAGE INSTRUCTIONS:")
    print("1. Open a new terminal window")
    print("2. Run one of the capture scripts above")
    print("3. Activate sensors (TXT button or Num Lock)")
    print("4. Watch data being captured to files")
    print("5. Use this script to parse the captured files")
    
    print(f"\n🔍 TO PARSE CAPTURED FILES:")
    print("python3 file_capture_sensors.py --parse /path/to/captured/file.txt")
    
    # Check for existing captured files
    print(f"\n📁 CHECKING FOR EXISTING CAPTURED FILES:")
    capture_files = []
    for pattern in ["/tmp/temperhum_*.txt", "/tmp/temperhum_*.json"]:
        try:
            files = subprocess.run(f"ls {pattern}", shell=True, capture_output=True, text=True)
            if files.returncode == 0:
                capture_files.extend(files.stdout.strip().split('\n'))
        except:
            pass
    
    if capture_files:
        print("Found existing capture files:")
        for file in capture_files:
            if file.strip():
                print(f"  {file}")
    else:
        print("No existing capture files found")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 