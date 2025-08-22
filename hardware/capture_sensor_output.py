#!/usr/bin/env python3
"""
TEMPerHUM Sensor Output Capture
===============================

This script captures output from TEMPerHUM sensors by monitoring input devices.
It's designed to work when sensors are "typing" their readings.

Usage:
    python3 capture_sensor_output.py
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime

def run_cmd(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def find_temperhum_devices():
    """Find TEMPerHUM input devices."""
    print("🔍 Finding TEMPerHUM input devices...")
    
    # Get input devices
    output, code = run_cmd("ls /dev/input/event*")
    if code != 0:
        print("❌ No input devices found")
        return []
    
    devices = []
    for device in output.split('\n'):
        if device.strip():
            # Check if this device is associated with TEMPerHUM
            info_cmd = f"udevadm info -q property {device}"
            info_output, _ = run_cmd(info_cmd)
            
            if "3553:a001" in info_output or "TEMPerHUM" in info_output:
                devices.append(device.strip())
                print(f"✅ TEMPerHUM device found: {device}")
    
    return devices

def capture_from_device(device_path, duration=30):
    """Capture input from a specific device."""
    print(f"📥 Capturing from {device_path} for {duration} seconds...")
    
    # Use evtest to capture raw input
    capture_cmd = f"timeout {duration} evtest {device_path} 2>/dev/null | head -20"
    output, code = run_cmd(capture_cmd)
    
    if output:
        print(f"📊 Raw capture from {device_path}:")
        print(output[:200] + "..." if len(output) > 200 else output)
        return output
    else:
        print(f"❌ No output captured from {device_path}")
        return None

def try_temper_py():
    """Try to read using temper-py."""
    print("🔧 Trying temper-py...")
    
    # Try different temper-py commands
    commands = [
        "temper.py",
        "python3 -m temper",
        "temper.py --list",
        "python3 -m temper --list"
    ]
    
    for cmd in commands:
        output, code = run_cmd(cmd)
        if code == 0 and output:
            print(f"✅ {cmd} output: {output}")
            return output
    
    print("❌ temper-py not working")
    return None

def manual_capture():
    """Manual capture with user input."""
    print("\n🎯 Manual Capture Mode")
    print("Press TXT button on sensors or hold Caps Lock for 3 seconds")
    print("Then type what you see on the remote machine's screen:")
    
    captured_data = []
    
    for i in range(3):  # Try 3 times
        try:
            print(f"\n--- Attempt {i+1} ---")
            user_input = input("Sensor output (or 'skip'): ").strip()
            
            if user_input.lower() == 'skip':
                continue
            
            if user_input:
                captured_data.append({
                    'timestamp': datetime.now().isoformat(),
                    'raw_data': user_input,
                    'attempt': i+1
                })
                print(f"✅ Captured: {user_input}")
            
        except KeyboardInterrupt:
            print("\n⏹️ Capture interrupted")
            break
    
    return captured_data

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
    """Main capture function."""
    print("🐢 TEMPerHUM Sensor Output Capture")
    print("=" * 50)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'captures': []
    }
    
    # Method 1: Try temper-py
    temper_output = try_temper_py()
    if temper_output:
        parsed = parse_sensor_data(temper_output)
        if parsed:
            results['captures'].append({
                'method': 'temper-py',
                'data': parsed,
                'raw_output': temper_output
            })
    
    # Method 2: Find and capture from input devices
    devices = find_temperhum_devices()
    for device in devices:
        output = capture_from_device(device, duration=10)
        if output:
            # Look for any readable data in the output
            lines = output.split('\n')
            for line in lines:
                if any(char.isdigit() for char in line):
                    parsed = parse_sensor_data(line)
                    if parsed:
                        results['captures'].append({
                            'method': 'device-capture',
                            'device': device,
                            'data': parsed,
                            'raw_output': line
                        })
    
    # Method 3: Manual capture
    manual_data = manual_capture()
    for capture in manual_data:
        parsed = parse_sensor_data(capture['raw_data'])
        if parsed:
            results['captures'].append({
                'method': 'manual',
                'data': parsed,
                'raw_output': capture['raw_data'],
                'timestamp': capture['timestamp']
            })
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/tmp/temperhum_capture_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Display summary
    print("\n" + "=" * 50)
    print("📊 CAPTURE SUMMARY")
    print("=" * 50)
    
    if results['captures']:
        print(f"✅ Successfully captured {len(results['captures'])} readings:")
        for i, capture in enumerate(results['captures'], 1):
            data = capture['data']
            print(f"  {i}. {capture['method']}: {data['temperature']}°C, {data['humidity']}%")
            print(f"     Raw: {capture['raw_output']}")
    else:
        print("❌ No sensor data captured")
        print("💡 Try:")
        print("   - Press TXT button on sensors")
        print("   - Hold Caps Lock for 3 seconds")
        print("   - Check if sensors are in correct mode")
    
    print(f"\n📁 Results saved to: {filename}")
    
    return len(results['captures']) > 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Capture interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 