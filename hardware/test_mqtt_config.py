#!/usr/bin/env python3
"""
Test script to check MQTT service configuration loading
"""

import os
import sys
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from temperhum_mqtt_service import TemperhUMMQTTService
    
    print("Testing MQTT service configuration loading...")
    
    # Create service instance
    service = TemperhUMMQTTService()
    
    # Check configuration
    temp_unit = service.config.get('service', {}).get('temperature_unit', 'unknown')
    print(f"Temperature unit from config: {temp_unit}")
    
    # Check controller temperature unit
    controller_temp_unit = service.controller.temperature_unit
    print(f"Controller temperature unit: {controller_temp_unit}")
    
    # Check if they match
    if temp_unit == controller_temp_unit:
        print("✅ Configuration and controller temperature units match!")
    else:
        print("❌ Configuration and controller temperature units don't match!")
    
    # Test sensor reading
    print("\nTesting sensor reading...")
    readings = service.read_sensors()
    
    if readings:
        for sensor_id, data in readings.items():
            print(f"\nSensor {sensor_id}:")
            print(f"  Temperature: {data.get('internal_temperature', 'N/A')}")
            print(f"  Temperature (°C): {data.get('internal_temperature_c', 'N/A')}")
            print(f"  Temperature (°F): {data.get('internal_temperature_f', 'N/A')}")
            print(f"  Humidity: {data.get('internal_humidity', 'N/A')}")
    else:
        print("No sensor readings available")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}") 