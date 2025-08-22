#!/usr/bin/env python3
"""
Optimized TEMPerHUM Sensor Capture
==================================

Based on local testing, this script captures the exact format:
29.16 [c]36.08 [%rh]1s

Usage:
    python3 optimized_temperhum_capture.py
"""

import os
import sys
import time
import json
import subprocess
import re
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
    
    # Check USB devices
    output, code = run_cmd("lsusb")
    if code != 0:
        return []
    
    devices = []
    for line in output.split('\n'):
        if "3553:a001" in line and "TEMPerHUM" in line:
            devices.append(line.strip())
            print(f"✅ TEMPerHUM found: {line.strip()}")
    
    return devices

def capture_sensor_data(duration=60):
    """Capture sensor data using the discovered format."""
    print(f"📥 Capturing sensor data for {duration} seconds...")
    print("Press TXT button on sensors or hold Caps Lock for 3 seconds to start...")
    
    # Create a temporary file to capture output
    temp_file = "/tmp/temperhum_raw_capture.txt"
    
    # Start capture in background
    capture_cmd = f"timeout {duration} cat > {temp_file}"
    
    print("Starting capture...")
    print("The sensors will type data like: 29.16 [c]36.08 [%rh]1s")
    print("Press Ctrl+C to stop early...")
    
    try:
        # Run capture command
        process = subprocess.Popen(capture_cmd, shell=True, stdin=subprocess.PIPE)
        
        # Wait for user to activate sensors
        input("Press Enter when sensors are activated and typing...")
        
        # Let it capture for a while
        time.sleep(30)
        
        # Stop capture
        process.terminate()
        process.wait(timeout=5)
        
    except KeyboardInterrupt:
        print("\n⏹️ Capture stopped by user")
        if process:
            process.terminate()
    
    # Read captured data
    captured_data = []
    if os.path.exists(temp_file):
        with open(temp_file, 'r') as f:
            raw_data = f.read()
        
        # Parse the data using the exact format we discovered
        lines = raw_data.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                parsed = parse_temperhum_data(line)
                if parsed:
                    captured_data.append({
                        'timestamp': datetime.now().isoformat(),
                        'raw_data': line,
                        'parsed': parsed
                    })
    
    return captured_data

def parse_temperhum_data(raw_data):
    """Parse TEMPerHUM data in the exact format we discovered."""
    # Format: 29.16 [c]36.08 [%rh]1s
    pattern = r'(\d+\.?\d*)\s*\[c\](\d+\.?\d*)\s*\[%rh\](\d+)s'
    
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
            pass
    
    return None

def test_manual_input():
    """Test manual input with the exact format."""
    print("\n🎯 Manual Input Test")
    print("=" * 50)
    print("Please type the sensor output in the exact format:")
    print("Example: 29.16 [c]36.08 [%rh]1s")
    
    captured_data = []
    
    for i in range(5):  # Test 5 times
        try:
            print(f"\n--- Test {i+1} ---")
            user_input = input("Sensor output (or 'skip'): ").strip()
            
            if user_input.lower() == 'skip':
                continue
            
            parsed = parse_temperhum_data(user_input)
            if parsed:
                captured_data.append({
                    'timestamp': datetime.now().isoformat(),
                    'raw_data': user_input,
                    'parsed': parsed
                })
                print(f"✅ Parsed: {parsed['temperature']}°C, {parsed['humidity']}%")
            else:
                print("❌ Could not parse data")
            
        except KeyboardInterrupt:
            print("\n⏹️ Test interrupted")
            break
    
    return captured_data

def create_remote_capture_script():
    """Create a script optimized for remote deployment."""
    script_content = '''#!/usr/bin/env python3
"""
Remote TEMPerHUM Capture Script
===============================

Optimized for remote deployment based on local testing.
Captures the exact format: 29.16 [c]36.08 [%rh]1s
"""

import os
import sys
import time
import json
import subprocess
import re
from datetime import datetime

def parse_temperhum_data(raw_data):
    """Parse TEMPerHUM data in the exact format."""
    pattern = r'(\\d+\\.?\\d*)\\s*\\[c\\](\\d+\\.?\\d*)\\s*\\[%rh\\](\\d+)s'
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
            pass
    return None

def capture_sensors():
    """Capture sensor data."""
    print("🐢 TEMPerHUM Remote Capture")
    print("=" * 40)
    
    # Check for sensors
    result = subprocess.run("lsusb | grep -i temperhum", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ No TEMPerHUM sensors found")
        return []
    
    print("✅ TEMPerHUM sensors detected")
    print("Press TXT button on sensors or hold Caps Lock for 3 seconds")
    
    # Create capture file
    capture_file = "/tmp/temperhum_remote_capture.txt"
    
    print("Starting capture...")
    print("Type 'quit' to stop")
    
    captured_data = []
    
    try:
        while True:
            line = input().strip()
            if line.lower() == 'quit':
                break
            
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
    
    except KeyboardInterrupt:
        print("\\n⏹️ Capture stopped")
    
    return captured_data

if __name__ == "__main__":
    data = capture_sensors()
    
    if data:
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/temperhum_remote_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\\n📁 Saved {len(data)} readings to {filename}")
        
        # Display summary
        if data:
            temps = [d['temperature'] for d in data]
            hums = [d['humidity'] for d in data]
            print(f"📊 Summary: Temp {min(temps):.1f}-{max(temps):.1f}°C, Humidity {min(hums):.1f}-{max(hums):.1f}%")
    else:
        print("❌ No data captured")
'''
    
    with open('/tmp/remote_temperhum_capture.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Remote capture script created: /tmp/remote_temperhum_capture.py")

def main():
    """Main function."""
    print("🐢 Optimized TEMPerHUM Capture")
    print("=" * 50)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'format_discovered': '29.16 [c]36.08 [%rh]1s',
        'captures': []
    }
    
    # Check devices
    devices = find_temperhum_devices()
    if not devices:
        print("❌ No TEMPerHUM devices found")
        return False
    
    # Test manual input
    print("\n1️⃣ Testing Manual Input")
    manual_data = test_manual_input()
    results['captures'].extend(manual_data)
    
    # Create remote script
    print("\n2️⃣ Creating Remote Script")
    create_remote_capture_script()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"temperhum_optimized_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display summary
    print("\n" + "=" * 50)
    print("📊 OPTIMIZATION SUMMARY")
    print("=" * 50)
    
    if results['captures']:
        print(f"✅ Successfully captured {len(results['captures'])} readings")
        for i, capture in enumerate(results['captures'], 1):
            parsed = capture['parsed']
            print(f"  {i}. {parsed['temperature']}°C, {parsed['humidity']}%")
            print(f"     Raw: {parsed['raw_data']}")
    
    print(f"\n📁 Results saved to: {filename}")
    print("✅ Remote script created: /tmp/remote_temperhum_capture.py")
    
    print("\n💡 NEXT STEPS:")
    print("1. Deploy /tmp/remote_temperhum_capture.py to remote machine")
    print("2. Run it on remote machine")
    print("3. Activate sensors with TXT button or Caps Lock")
    print("4. Capture the data in the exact format we discovered")
    
    return len(results['captures']) > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 