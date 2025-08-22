#!/usr/bin/env python3
"""
Dual TEMPerHUM Sensor Testing
=============================

Tests two TEMPerHUM sensors separately and finds reliable triggering methods.
Each sensor measures distinct areas and needs to be handled independently.

Usage:
    python3 dual_sensor_test.py
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
    """Find and identify individual TEMPerHUM sensors."""
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

def test_triggering_methods():
    """Test different triggering methods with immediate feedback."""
    print("\n🎯 Testing Triggering Methods")
    print("=" * 50)
    
    methods = [
        {
            'name': 'Caps Lock Hold (3 seconds)',
            'description': 'Hold Caps Lock key for 3 seconds',
            'instructions': 'Hold Caps Lock for exactly 3 seconds, then release'
        },
        {
            'name': 'Caps Lock Toggle',
            'description': 'Press Caps Lock once to toggle',
            'instructions': 'Press Caps Lock once, wait for response'
        },
        {
            'name': 'TXT Button (Sensor 1)',
            'description': 'Press TXT button on first sensor',
            'instructions': 'Press the TXT button on the first TEMPerHUM sensor'
        },
        {
            'name': 'TXT Button (Sensor 2)',
            'description': 'Press TXT button on second sensor',
            'instructions': 'Press the TXT button on the second TEMPerHUM sensor'
        },
        {
            'name': 'Num Lock Hold (3 seconds)',
            'description': 'Hold Num Lock key for 3 seconds',
            'instructions': 'Hold Num Lock for exactly 3 seconds, then release'
        },
        {
            'name': 'Num Lock Toggle',
            'description': 'Press Num Lock once to toggle',
            'instructions': 'Press Num Lock once, wait for response'
        }
    ]
    
    results = []
    
    for i, method in enumerate(methods, 1):
        print(f"\n--- Method {i}: {method['name']} ---")
        print(f"Description: {method['description']}")
        print(f"Instructions: {method['instructions']}")
        
        # Wait for user to try the method
        input("Press Enter when ready to test this method...")
        
        print("⏳ Testing now... (watch for sensor output)")
        print("Type what you see, or 'skip' if nothing happens:")
        
        # Capture the output
        try:
            user_input = input("Sensor output: ").strip()
            
            if user_input.lower() != 'skip':
                result = {
                    'method': method['name'],
                    'description': method['description'],
                    'output': user_input,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
                results.append(result)
                print(f"✅ Captured: {user_input}")
            else:
                result = {
                    'method': method['name'],
                    'description': method['description'],
                    'output': None,
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
                results.append(result)
                print("❌ No output detected")
                
        except KeyboardInterrupt:
            print("⏹️ Test interrupted")
            break
    
    return results

def test_sensor_separation():
    """Test if we can identify which sensor is which."""
    print("\n🔍 Testing Sensor Separation")
    print("=" * 50)
    
    print("We need to identify which sensor is which.")
    print("Let's test each sensor individually:")
    
    sensor_data = {}
    
    # Test Sensor 1
    print("\n--- Testing Sensor 1 ---")
    print("Instructions:")
    print("1. Unplug Sensor 2 (if possible)")
    print("2. Or cover Sensor 2's TXT button")
    print("3. Press TXT button on Sensor 1 only")
    print("4. Tell us what you see")
    
    input("Press Enter when ready...")
    sensor1_output = input("Sensor 1 output: ").strip()
    
    if sensor1_output.lower() != 'skip':
        sensor_data['sensor_1'] = {
            'output': sensor1_output,
            'timestamp': datetime.now().isoformat()
        }
        print(f"✅ Sensor 1: {sensor1_output}")
    
    # Test Sensor 2
    print("\n--- Testing Sensor 2 ---")
    print("Instructions:")
    print("1. Unplug Sensor 1 (if possible)")
    print("2. Or cover Sensor 1's TXT button")
    print("3. Press TXT button on Sensor 2 only")
    print("4. Tell us what you see")
    
    input("Press Enter when ready...")
    sensor2_output = input("Sensor 2 output: ").strip()
    
    if sensor2_output.lower() != 'skip':
        sensor_data['sensor_2'] = {
            'output': sensor2_output,
            'timestamp': datetime.now().isoformat()
        }
        print(f"✅ Sensor 2: {sensor2_output}")
    
    return sensor_data

def test_continuous_capture():
    """Test capturing continuous data from both sensors."""
    print("\n📊 Testing Continuous Capture")
    print("=" * 50)
    
    print("This will test capturing continuous data from both sensors.")
    print("We'll try to identify which data comes from which sensor.")
    
    print("\nInstructions:")
    print("1. Activate both sensors (use the best method we discovered)")
    print("2. Let them type for 30 seconds")
    print("3. We'll try to separate the data streams")
    
    input("Press Enter when ready to start continuous capture...")
    
    print("⏳ Starting 30-second capture...")
    print("Activate your sensors now!")
    
    # Create a simple capture mechanism
    captured_lines = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < 30:
            try:
                line = input().strip()
                if line:
                    captured_lines.append({
                        'timestamp': datetime.now().isoformat(),
                        'data': line,
                        'elapsed': time.time() - start_time
                    })
                    print(f"📥 {line}")
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\n⏹️ Capture stopped by user")
    
    return captured_lines

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

def analyze_captured_data(captured_lines):
    """Analyze captured data to identify patterns and separate sensors."""
    print("\n🔬 Analyzing Captured Data")
    print("=" * 50)
    
    parsed_data = []
    unparsed_data = []
    
    for line_data in captured_lines:
        raw_data = line_data['data']
        parsed = parse_temperhum_data(raw_data)
        
        if parsed:
            parsed_data.append({
                'timestamp': line_data['timestamp'],
                'elapsed': line_data['elapsed'],
                'parsed': parsed,
                'raw_data': raw_data
            })
        else:
            unparsed_data.append({
                'timestamp': line_data['timestamp'],
                'elapsed': line_data['elapsed'],
                'raw_data': raw_data
            })
    
    print(f"📊 Analysis Results:")
    print(f"  Total lines captured: {len(captured_lines)}")
    print(f"  Parsed sensor data: {len(parsed_data)}")
    print(f"  Unparsed data: {len(unparsed_data)}")
    
    if parsed_data:
        print(f"\n📈 Sensor Data Summary:")
        temps = [d['parsed']['temperature'] for d in parsed_data]
        hums = [d['parsed']['humidity'] for d in parsed_data]
        
        print(f"  Temperature range: {min(temps):.1f}°C - {max(temps):.1f}°C")
        print(f"  Humidity range: {min(hums):.1f}% - {max(hums):.1f}%")
        print(f"  Average temperature: {sum(temps)/len(temps):.1f}°C")
        print(f"  Average humidity: {sum(hums)/len(hums):.1f}%")
        
        print(f"\n📋 All parsed readings:")
        for i, data in enumerate(parsed_data, 1):
            parsed = data['parsed']
            print(f"  {i}. {parsed['temperature']}°C, {parsed['humidity']}% (t+{data['elapsed']:.1f}s)")
    
    if unparsed_data:
        print(f"\n📝 Unparsed data:")
        for i, data in enumerate(unparsed_data, 1):
            print(f"  {i}. {data['raw_data']} (t+{data['elapsed']:.1f}s)")
    
    return {
        'parsed_data': parsed_data,
        'unparsed_data': unparsed_data,
        'total_captured': len(captured_lines)
    }

def main():
    """Main testing function."""
    print("🐢 Dual TEMPerHUM Sensor Testing")
    print("=" * 50)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'test_session': 'dual_sensor_analysis',
        'findings': {}
    }
    
    # Step 1: Find devices
    print("\n1️⃣ Device Detection")
    devices = find_temperhum_devices()
    results['findings']['devices'] = devices
    
    if len(devices) < 2:
        print("⚠️ Warning: Less than 2 sensors detected")
        print("Make sure both sensors are plugged in")
    
    # Step 2: Test triggering methods
    print("\n2️⃣ Triggering Method Testing")
    trigger_results = test_triggering_methods()
    results['findings']['triggering_methods'] = trigger_results
    
    # Step 3: Test sensor separation
    print("\n3️⃣ Sensor Separation Testing")
    sensor_separation = test_sensor_separation()
    results['findings']['sensor_separation'] = sensor_separation
    
    # Step 4: Test continuous capture
    print("\n4️⃣ Continuous Capture Testing")
    continuous_data = test_continuous_capture()
    results['findings']['continuous_capture'] = continuous_data
    
    # Step 5: Analyze data
    print("\n5️⃣ Data Analysis")
    analysis = analyze_captured_data(continuous_data)
    results['findings']['analysis'] = analysis
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dual_sensor_test_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    print(f"✅ Devices found: {len(devices)}")
    
    working_methods = [m for m in trigger_results if m['success']]
    print(f"✅ Working triggering methods: {len(working_methods)}")
    
    if working_methods:
        print("🎯 Best triggering methods:")
        for method in working_methods:
            print(f"  - {method['method']}: {method['output']}")
    
    if analysis['parsed_data']:
        print(f"✅ Sensor data captured: {len(analysis['parsed_data'])} readings")
    
    print(f"\n📁 Results saved to: {filename}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if working_methods:
        best_method = working_methods[0]
        print(f"✅ Use '{best_method['method']}' for reliable triggering")
    
    if analysis['parsed_data']:
        print("✅ Sensors are working and producing valid data")
        print("✅ Ready for dual-sensor remote deployment")
    
    return len(working_methods) > 0 and len(analysis['parsed_data']) > 0

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