#!/usr/bin/env python3
"""
Get TEMPerHUM Sensor Readings
=============================

This script helps you get actual temperature and humidity readings
from your TEMPerHUM sensors by guiding you through the correct
activation sequence.

Usage:
    python3 get_sensor_readings.py
"""

import time
import json
from datetime import datetime

def get_sensor_readings():
    """Guide user through getting sensor readings."""
    print("🐢 TEMPerHUM Sensor Reading Guide")
    print("=" * 50)
    
    readings = []
    
    print("\n📋 Instructions:")
    print("1. Make sure sensors are plugged in and powered (LED on)")
    print("2. Follow the prompts to activate each sensor")
    print("3. Type exactly what you see on screen")
    print("4. We'll parse the temperature and humidity data")
    
    input("\nPress Enter to continue...")
    
    # Test first sensor
    print("\n" + "="*30)
    print("SENSOR 1 TESTING")
    print("="*30)
    
    print("\n1️⃣ Press TXT button on first sensor:")
    sensor1_txt = input("What do you see? (or 'skip'): ").strip()
    
    print("\n2️⃣ Hold Caps Lock for 3 seconds:")
    sensor1_caps = input("What do you see? (or 'skip'): ").strip()
    
    print("\n3️⃣ Hold Num Lock for 3 seconds:")
    sensor1_num = input("What do you see? (or 'skip'): ").strip()
    
    # Test second sensor
    print("\n" + "="*30)
    print("SENSOR 2 TESTING")
    print("="*30)
    
    print("\n4️⃣ Press TXT button on second sensor:")
    sensor2_txt = input("What do you see? (or 'skip'): ").strip()
    
    print("\n5️⃣ Hold Caps Lock for 3 seconds:")
    sensor2_caps = input("What do you see? (or 'skip'): ").strip()
    
    print("\n6️⃣ Hold Num Lock for 3 seconds:")
    sensor2_num = input("What do you see? (or 'skip'): ").strip()
    
    # Collect all outputs
    outputs = [
        ("Sensor 1 TXT", sensor1_txt),
        ("Sensor 1 Caps", sensor1_caps),
        ("Sensor 1 Num", sensor1_num),
        ("Sensor 2 TXT", sensor2_txt),
        ("Sensor 2 Caps", sensor2_caps),
        ("Sensor 2 Num", sensor2_num)
    ]
    
    # Parse for temperature/humidity data
    print("\n" + "="*50)
    print("📊 PARSING RESULTS")
    print("="*50)
    
    for name, output in outputs:
        if output.lower() != 'skip' and output.strip():
            print(f"\n{name}: {output}")
            
            # Look for temperature/humidity patterns
            if any(char.isdigit() for char in output):
                print(f"  🔍 Contains numbers - might be sensor data")
                
                # Check for common patterns
                if '°C' in output or 'C' in output:
                    print(f"  🌡️ Contains temperature data")
                if '%' in output or 'RH' in output:
                    print(f"  💧 Contains humidity data")
                
                readings.append({
                    'method': name,
                    'output': output,
                    'timestamp': datetime.now().isoformat()
                })
    
    return readings

def parse_temperature_humidity(text):
    """Parse temperature and humidity from text."""
    import re
    
    # Common TEMPerHUM patterns
    patterns = [
        # Format: "32.73[C]36.82[%RH]1S"
        r'(\d+\.?\d*)\[C\](\d+\.?\d*)\[%RH\](\d+)S',
        # Format: "32.73°C 36.82%"
        r'(\d+\.?\d*)°C\s+(\d+\.?\d*)%',
        # Format: "32.73C 36.82%"
        r'(\d+\.?\d*)C\s+(\d+\.?\d*)%',
        # Format: "Temp: 32.73°C, Humidity: 36.82%"
        r'Temp:\s*(\d+\.?\d*)°C.*Humidity:\s*(\d+\.?\d*)%',
        # Format: "32.73 36.82"
        r'(\d+\.?\d*)\s+(\d+\.?\d*)',
        # Format: "32.73C36.82%"
        r'(\d+\.?\d*)C(\d+\.?\d*)%',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                temp = float(match.group(1))
                humidity = float(match.group(2))
                return {
                    'temperature': temp,
                    'humidity': humidity,
                    'raw_data': text
                }
            except (ValueError, IndexError):
                continue
    
    return None

def main():
    """Main function."""
    print("🔍 Getting TEMPerHUM Sensor Readings")
    print("=" * 50)
    
    # Get readings
    readings = get_sensor_readings()
    
    if not readings:
        print("\n❌ No sensor data captured")
        print("💡 Try:")
        print("   - Make sure sensors are powered")
        print("   - Try different button combinations")
        print("   - Check if sensors are in data mode")
        return False
    
    # Parse readings
    print("\n" + "="*50)
    print("🔍 PARSING SENSOR DATA")
    print("="*50)
    
    parsed_readings = []
    
    for reading in readings:
        parsed = parse_temperature_humidity(reading['output'])
        if parsed:
            parsed_readings.append({
                'method': reading['method'],
                'temperature': parsed['temperature'],
                'humidity': parsed['humidity'],
                'raw_data': parsed['raw_data'],
                'timestamp': reading['timestamp']
            })
            print(f"✅ {reading['method']}: {parsed['temperature']}°C, {parsed['humidity']}%")
            print(f"   Raw: {parsed['raw_data']}")
        else:
            print(f"❌ {reading['method']}: No temperature/humidity data found")
            print(f"   Raw: {reading['output']}")
    
    # Save results
    if parsed_readings:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temperhum_readings_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(parsed_readings, f, indent=2)
        
        print(f"\n📁 Sensor readings saved to: {filename}")
        
        # Summary
        print(f"\n🎉 Successfully captured {len(parsed_readings)} sensor readings!")
        
        # Show recommendations for remote deployment
        print("\n💡 REMOTE DEPLOYMENT RECOMMENDATIONS:")
        print("✅ Use manual capture method (sensors type their output)")
        print("✅ Parse format: Look for temperature and humidity patterns")
        print("✅ Handle multiple activation methods (TXT, Caps Lock, Num Lock)")
        print("✅ Save raw data for debugging")
        
        return True
    else:
        print("\n❌ No temperature/humidity data found")
        print("💡 The sensors might be in identification mode")
        print("   Try different activation sequences or check sensor documentation")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1) 