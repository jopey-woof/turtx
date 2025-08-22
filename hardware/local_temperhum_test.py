#!/usr/bin/env python3
"""
Local TEMPerHUM Sensor Testing
==============================

This script tests TEMPerHUM sensors on your local machine to understand
their behavior and output formats. Run this after plugging in your sensors.

Usage:
    python3 local_temperhum_test.py
"""

import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime

def run_cmd(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def check_usb_devices():
    """Check for TEMPerHUM USB devices."""
    print("🔍 Checking USB devices...")
    
    output, code = run_cmd("lsusb")
    if code != 0:
        print("❌ Failed to run lsusb")
        return []
    
    temperhum_ids = ["413d:2107", "1a86:e025", "3553:a001", "0c45:7401", "0c45:7402"]
    found = []
    
    for line in output.split('\n'):
        if any(id_pair in line for id_pair in temperhum_ids):
            found.append(line.strip())
            print(f"✅ TEMPerHUM detected: {line.strip()}")
    
    return found

def check_input_devices():
    """Check for TEMPerHUM input devices."""
    print("\n🔍 Checking input devices...")
    
    output, code = run_cmd("ls /dev/input/event*")
    if code != 0:
        print("❌ No input devices found")
        return []
    
    devices = []
    for device in output.split('\n'):
        if device.strip():
            # Get device info
            info_cmd = f"udevadm info -q property {device}"
            info_output, _ = run_cmd(info_cmd)
            
            if "3553:a001" in info_output or "TEMPerHUM" in info_output:
                devices.append(device.strip())
                print(f"✅ TEMPerHUM input device: {device}")
    
    return devices

def test_temper_py():
    """Test temper-py functionality."""
    print("\n🔧 Testing temper-py...")
    
    # Check if temper-py is installed
    try:
        import temper
        print("✅ temper-py imported successfully")
    except ImportError:
        print("❌ temper-py not installed")
        print("💡 Install with: pip3 install temper-py")
        return False
    
    # Test different commands
    commands = [
        "temper.py",
        "python3 -m temper",
        "temper.py --list",
        "python3 -m temper --list"
    ]
    
    for cmd in commands:
        output, code = run_cmd(cmd)
        if code == 0 and output:
            print(f"✅ {cmd} working:")
            print(f"   Output: {output[:100]}...")
            return True
    
    print("❌ temper-py commands not working")
    return False

def capture_keyboard_input():
    """Capture keyboard input from sensors."""
    print("\n⌨️  Keyboard Input Capture Test")
    print("=" * 50)
    print("This will capture any keyboard input for 30 seconds.")
    print("Press TXT button on sensors or hold Caps Lock for 3 seconds.")
    print("Press Ctrl+C to stop early.")
    print("\nStarting capture in 3 seconds...")
    
    time.sleep(3)
    
    captured_data = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < 30:
            # Read from stdin (this is a simplified approach)
            if sys.stdin.isatty():
                print("⏳ Waiting for sensor input... (Press Ctrl+C to stop)")
                time.sleep(2)
            else:
                # If not a TTY, try to read input
                try:
                    line = input()
                    if line.strip():
                        captured_data.append({
                            'timestamp': datetime.now().isoformat(),
                            'data': line.strip()
                        })
                        print(f"📥 Captured: {line.strip()}")
                except EOFError:
                    break
    except KeyboardInterrupt:
        print("\n⏹️ Capture stopped by user")
    
    return captured_data

def test_evtest_capture():
    """Test capturing with evtest."""
    print("\n📡 Testing evtest capture...")
    
    devices = check_input_devices()
    if not devices:
        print("❌ No TEMPerHUM input devices found")
        return []
    
    captured_data = []
    
    for device in devices:
        print(f"\n📥 Capturing from {device}...")
        print("Press TXT button on sensor now...")
        
        # Use evtest to capture raw input
        cmd = f"timeout 10 evtest {device} 2>/dev/null"
        output, code = run_cmd(cmd)
        
        if output:
            print(f"📊 Raw evtest output from {device}:")
            print(output[:300] + "..." if len(output) > 300 else output)
            captured_data.append({
                'device': device,
                'output': output,
                'timestamp': datetime.now().isoformat()
            })
        else:
            print(f"❌ No output from {device}")
    
    return captured_data

def interactive_test():
    """Interactive testing with user input."""
    print("\n🎯 Interactive Testing")
    print("=" * 50)
    print("Please test the sensors manually and tell me what you see:")
    
    results = []
    
    print("\n1. Press TXT button on first sensor:")
    sensor1_output = input("What do you see? (or 'skip'): ").strip()
    if sensor1_output.lower() != 'skip':
        results.append({
            'sensor': 1,
            'method': 'TXT button',
            'output': sensor1_output,
            'timestamp': datetime.now().isoformat()
        })
    
    print("\n2. Hold Caps Lock for 3 seconds:")
    caps_output = input("What do you see? (or 'skip'): ").strip()
    if caps_output.lower() != 'skip':
        results.append({
            'sensor': 'both',
            'method': 'Caps Lock',
            'output': caps_output,
            'timestamp': datetime.now().isoformat()
        })
    
    print("\n3. Press TXT button on second sensor:")
    sensor2_output = input("What do you see? (or 'skip'): ").strip()
    if sensor2_output.lower() != 'skip':
        results.append({
            'sensor': 2,
            'method': 'TXT button',
            'output': sensor2_output,
            'timestamp': datetime.now().isoformat()
        })
    
    return results

def parse_sensor_data(raw_data):
    """Parse sensor data from various formats."""
    import re
    
    patterns = [
        # Format: "32.73[C]36.82[%RH]1S"
        r'(\d+\.?\d*)\[C\](\d+\.?\d*)\[%RH\](\d+)S',
        # Format: "32.73°C 36.82%"
        r'(\d+\.?\d*)°C\s+(\d+\.?\d*)%',
        # Format: "Temp: 32.73°C, Humidity: 36.82%"
        r'Temp:\s*(\d+\.?\d*)°C.*Humidity:\s*(\d+\.?\d*)%',
        # Format: "32.73 36.82"
        r'(\d+\.?\d*)\s+(\d+\.?\d*)',
        # Format: "32.73C36.82%"
        r'(\d+\.?\d*)C(\d+\.?\d*)%',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, raw_data)
        if match:
            try:
                temp = float(match.group(1))
                humidity = float(match.group(2))
                return {
                    'temperature': temp,
                    'humidity': humidity,
                    'raw_data': raw_data
                }
            except (ValueError, IndexError):
                continue
    
    return None

def main():
    """Main testing function."""
    print("🐢 Local TEMPerHUM Sensor Testing")
    print("=" * 50)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'python_version': sys.version,
            'platform': os.uname().sysname if hasattr(os, 'uname') else 'Unknown'
        },
        'tests': {}
    }
    
    # Test 1: USB Detection
    print("\n1️⃣ USB Device Detection")
    usb_devices = check_usb_devices()
    results['tests']['usb_detection'] = {
        'success': len(usb_devices) > 0,
        'devices': usb_devices
    }
    
    # Test 2: Input Device Detection
    print("\n2️⃣ Input Device Detection")
    input_devices = check_input_devices()
    results['tests']['input_detection'] = {
        'success': len(input_devices) > 0,
        'devices': input_devices
    }
    
    # Test 3: temper-py
    print("\n3️⃣ temper-py Testing")
    temper_success = test_temper_py()
    results['tests']['temper_py'] = {
        'success': temper_success
    }
    
    # Test 4: evtest Capture
    print("\n4️⃣ evtest Capture Testing")
    evtest_data = test_evtest_capture()
    results['tests']['evtest_capture'] = {
        'success': len(evtest_data) > 0,
        'data': evtest_data
    }
    
    # Test 5: Interactive Testing
    print("\n5️⃣ Interactive Testing")
    interactive_data = interactive_test()
    results['tests']['interactive'] = {
        'success': len(interactive_data) > 0,
        'data': interactive_data
    }
    
    # Parse any captured data
    print("\n6️⃣ Data Parsing")
    parsed_data = []
    for test_name, test_data in results['tests'].items():
        if 'data' in test_data:
            for item in test_data['data']:
                if 'output' in item:
                    parsed = parse_sensor_data(item['output'])
                    if parsed:
                        parsed_data.append({
                            'source': test_name,
                            'parsed': parsed,
                            'original': item
                        })
    
    results['parsed_data'] = parsed_data
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"temperhum_local_test_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, test_data in results['tests'].items():
        status = "✅ PASS" if test_data.get('success', False) else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    if parsed_data:
        print(f"\n🎉 Successfully parsed {len(parsed_data)} sensor readings:")
        for i, data in enumerate(parsed_data, 1):
            parsed = data['parsed']
            print(f"  {i}. {parsed['temperature']}°C, {parsed['humidity']}%")
            print(f"     Source: {data['source']}")
            print(f"     Raw: {parsed['raw_data']}")
    
    print(f"\n📁 Results saved to: {filename}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if len(usb_devices) > 0:
        print("✅ Sensors detected - ready for remote deployment")
    if len(parsed_data) > 0:
        print("✅ Data format understood - can implement parsing")
    if temper_success:
        print("✅ temper-py working - can use programmatic reading")
    else:
        print("⚠️ temper-py not working - will need manual capture method")
    
    return len(parsed_data) > 0

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