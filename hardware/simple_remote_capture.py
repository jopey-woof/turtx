#!/usr/bin/env python3
"""
Simple Remote TEMPerHUM Capture
===============================

Based on local testing, captures the exact format:
29.16 [c]36.08 [%rh]1s

Run this on the remote machine when sensors are plugged in.
"""

import os
import sys
import time
import json
import re
from datetime import datetime

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

def capture_sensors():
    """Capture sensor data from keyboard input."""
    print("🐢 TEMPerHUM Remote Capture")
    print("=" * 40)
    print("Based on local testing - captures format: 29.16 [c]36.08 [%rh]1s")
    print("")
    print("Instructions:")
    print("1. Make sure TEMPerHUM sensors are plugged in")
    print("2. Press TXT button on sensors or hold Caps Lock for 3 seconds")
    print("3. Type 'quit' to stop capture")
    print("4. Type 'test' to test parsing with sample data")
    print("")
    
    captured_data = []
    
    try:
        while True:
            line = input("Sensor output: ").strip()
            
            if line.lower() == 'quit':
                break
            
            if line.lower() == 'test':
                # Test with sample data
                test_data = "29.16 [c]36.08 [%rh]1s"
                parsed = parse_temperhum_data(test_data)
                if parsed:
                    print(f"✅ Test successful: {parsed['temperature']}°C, {parsed['humidity']}%")
                else:
                    print("❌ Test failed")
                continue
            
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
        print("\n⏹️ Capture stopped by user")
    
    return captured_data

def main():
    """Main function."""
    print("Starting TEMPerHUM capture...")
    
    # Check if sensors are present
    import subprocess
    result = subprocess.run("lsusb | grep -i temperhum", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ TEMPerHUM sensors detected")
        print(result.stdout.strip())
    else:
        print("⚠️ No TEMPerHUM sensors detected via lsusb")
        print("Make sure sensors are plugged in")
    
    print("")
    
    # Capture data
    data = capture_sensors()
    
    if data:
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/tmp/temperhum_remote_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n📁 Saved {len(data)} readings to {filename}")
        
        # Display summary
        if data:
            temps = [d['temperature'] for d in data]
            hums = [d['humidity'] for d in data]
            print(f"📊 Summary: Temp {min(temps):.1f}-{max(temps):.1f}°C, Humidity {min(hums):.1f}-{max(hums):.1f}%")
            
            print("\n📋 All readings:")
            for i, reading in enumerate(data, 1):
                print(f"  {i}. {reading['temperature']}°C, {reading['humidity']}% ({reading['raw_data']})")
    else:
        print("❌ No data captured")
    
    print("\n🎉 Capture complete!")

if __name__ == "__main__":
    main() 