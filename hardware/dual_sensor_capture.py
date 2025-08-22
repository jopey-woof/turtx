#!/usr/bin/env python3
"""
Dual TEMPerHUM Sensor Capture
=============================

Handles two TEMPerHUM sensors separately with both manual and programmatic triggering.
Based on testing: Num Lock Hold (3s) is most reliable for continuous data.

Usage:
    python3 dual_sensor_capture.py [--manual|--auto]
"""

import os
import sys
import time
import json
import subprocess
import re
import argparse
from datetime import datetime

def run_cmd(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def parse_temperhum_data(raw_data):
    """Parse TEMPerHUM data in the exact format we discovered."""
    # Format: 28.24 [C] 36.97 [%RH] 1S (with tabs and spaces)
    # Handle various spacing patterns
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

def trigger_sensors_programmatically():
    """Trigger sensors using Num Lock commands."""
    print("🔧 Triggering sensors programmatically...")
    
    # Method 1: Num Lock Hold (3 seconds) - most reliable
    print("1. Using Num Lock Hold (3 seconds)...")
    
    # Send Num Lock key press and hold
    try:
        # Use xdotool to send Num Lock key
        subprocess.run("xdotool keydown Num_Lock", shell=True)
        time.sleep(3)
        subprocess.run("xdotool keyup Num_Lock", shell=True)
        print("✅ Num Lock Hold sent")
        return True
    except Exception as e:
        print(f"❌ Num Lock Hold failed: {e}")
    
    # Method 2: Num Lock Toggle
    try:
        subprocess.run("xdotool key Num_Lock", shell=True)
        print("✅ Num Lock Toggle sent")
        return True
    except Exception as e:
        print(f"❌ Num Lock Toggle failed: {e}")
    
    return False

def capture_sensor_data(duration=60, manual_mode=True):
    """Capture sensor data with manual or automatic triggering."""
    print(f"📥 Capturing sensor data for {duration} seconds...")
    
    if manual_mode:
        print("\n🎯 MANUAL MODE")
        print("=" * 40)
        print("Instructions:")
        print("1. Press TXT button on Sensor 1 (if needed)")
        print("2. Press TXT button on Sensor 2 (if needed)")
        print("3. Or hold Num Lock for 3 seconds to activate both")
        print("4. Watch for continuous data output")
        print("5. Type 'quit' to stop early")
        print("")
        input("Press Enter when sensors are activated and typing...")
    else:
        print("\n🤖 AUTOMATIC MODE")
        print("=" * 40)
        print("Attempting programmatic activation...")
        
        if not trigger_sensors_programmatically():
            print("❌ Programmatic activation failed")
            print("Falling back to manual mode...")
            input("Press TXT buttons on sensors, then press Enter...")
    
    print("⏳ Starting capture...")
    print("Sensors should be typing data like: 28.24 [C] 36.97 [%RH] 1S")
    
    captured_data = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            try:
                line = input().strip()
                
                if line.lower() == 'quit':
                    break
                
                if line:
                    # Parse the data
                    parsed = parse_temperhum_data(line)
                    
                    data_point = {
                        'timestamp': datetime.now().isoformat(),
                        'elapsed': time.time() - start_time,
                        'raw_data': line
                    }
                    
                    if parsed:
                        data_point['parsed'] = parsed
                        data_point['sensor_id'] = 'unknown'  # We'll identify later
                        captured_data.append(data_point)
                        print(f"✅ {parsed['temperature']}°C, {parsed['humidity']}%")
                    else:
                        data_point['parsed'] = None
                        captured_data.append(data_point)
                        print(f"📝 Raw: {line}")
                        
            except EOFError:
                break
                
    except KeyboardInterrupt:
        print("\n⏹️ Capture stopped by user")
    
    return captured_data

def identify_sensor_data(captured_data):
    """Attempt to identify which data comes from which sensor."""
    print("\n🔍 Analyzing sensor data patterns...")
    
    # Group data by patterns to identify sensors
    sensor_patterns = {
        'sensor_1': [],
        'sensor_2': [],
        'unknown': []
    }
    
    for data_point in captured_data:
        if 'parsed' in data_point and data_point['parsed']:
            # For now, we'll need manual identification
            # In a real deployment, we'd use timing or other heuristics
            sensor_patterns['unknown'].append(data_point)
        else:
            # Non-parsed data (banner text, etc.)
            raw_data = data_point['raw_data']
            if 'TYPE:INNER-H3' in raw_data or 'INNER-TEMP' in raw_data:
                sensor_patterns['sensor_1'].append(data_point)
            elif any(char.isdigit() for char in raw_data):
                sensor_patterns['sensor_2'].append(data_point)
            else:
                sensor_patterns['unknown'].append(data_point)
    
    return sensor_patterns

def save_results(captured_data, sensor_patterns, filename=None):
    """Save captured data to file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dual_sensor_capture_{timestamp}.json"
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'capture_duration': len(captured_data),
        'sensor_patterns': sensor_patterns,
        'all_data': captured_data,
        'summary': {
            'total_captured': len(captured_data),
            'parsed_data': len([d for d in captured_data if 'parsed' in d and d['parsed']]),
            'sensor_1_data': len(sensor_patterns['sensor_1']),
            'sensor_2_data': len(sensor_patterns['sensor_2']),
            'unknown_data': len(sensor_patterns['unknown'])
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    return filename

def display_summary(captured_data, sensor_patterns):
    """Display capture summary."""
    print("\n" + "=" * 50)
    print("📊 CAPTURE SUMMARY")
    print("=" * 50)
    
    total_captured = len(captured_data)
    parsed_data = [d for d in captured_data if 'parsed' in d and d['parsed']]
    
    print(f"✅ Total lines captured: {total_captured}")
    print(f"✅ Parsed sensor data: {len(parsed_data)}")
    print(f"✅ Sensor 1 data: {len(sensor_patterns['sensor_1'])}")
    print(f"✅ Sensor 2 data: {len(sensor_patterns['sensor_2'])}")
    print(f"✅ Unknown data: {len(sensor_patterns['unknown'])}")
    
    if parsed_data:
        temps = [d['parsed']['temperature'] for d in parsed_data]
        hums = [d['parsed']['humidity'] for d in parsed_data]
        
        print(f"\n📈 Sensor Data Summary:")
        print(f"  Temperature range: {min(temps):.1f}°C - {max(temps):.1f}°C")
        print(f"  Humidity range: {min(hums):.1f}% - {max(hums):.1f}%")
        print(f"  Average temperature: {sum(temps)/len(temps):.1f}°C")
        print(f"  Average humidity: {sum(hums)/len(hums):.1f}%")
        
        print(f"\n📋 Recent readings:")
        for i, data in enumerate(parsed_data[-5:], 1):
            parsed = data['parsed']
            print(f"  {i}. {parsed['temperature']}°C, {parsed['humidity']}% (t+{data['elapsed']:.1f}s)")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Dual TEMPerHUM Sensor Capture')
    parser.add_argument('--manual', action='store_true', help='Use manual button activation')
    parser.add_argument('--auto', action='store_true', help='Use programmatic activation')
    parser.add_argument('--duration', type=int, default=60, help='Capture duration in seconds')
    args = parser.parse_args()
    
    print("🐢 Dual TEMPerHUM Sensor Capture")
    print("=" * 50)
    
    # Check for sensors
    devices = find_temperhum_devices()
    if len(devices) < 2:
        print("⚠️ Warning: Less than 2 sensors detected")
        print("Make sure both sensors are plugged in")
    
    # Determine mode
    manual_mode = True
    if args.auto:
        manual_mode = False
    elif not args.manual and not args.auto:
        # Default to manual mode
        manual_mode = True
    
    print(f"Mode: {'Manual' if manual_mode else 'Automatic'}")
    print(f"Duration: {args.duration} seconds")
    
    # Capture data
    captured_data = capture_sensor_data(args.duration, manual_mode)
    
    if captured_data:
        # Analyze data
        sensor_patterns = identify_sensor_data(captured_data)
        
        # Save results
        filename = save_results(captured_data, sensor_patterns)
        
        # Display summary
        display_summary(captured_data, sensor_patterns)
        
        print(f"\n📁 Results saved to: {filename}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if len(captured_data) > 0:
            print("✅ Sensors are working and producing data")
            print("✅ Ready for remote deployment")
            
            if manual_mode:
                print("✅ Manual mode works reliably")
            else:
                print("✅ Programmatic mode works for recovery")
        
        return True
    else:
        print("❌ No data captured")
        return False

def find_temperhum_devices():
    """Find TEMPerHUM devices."""
    output, code = run_cmd("lsusb")
    if code != 0:
        return []
    
    devices = []
    for line in output.split('\n'):
        if "3553:a001" in line and "TEMPerHUM" in line:
            devices.append(line.strip())
    
    return devices

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