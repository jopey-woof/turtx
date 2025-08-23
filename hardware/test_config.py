#!/usr/bin/env python3
"""
Test script to check TemperhUM configuration loading
"""
import os
import json
import sys

# Add the current directory to the path so we can import the service
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from temperhum_mqtt_service import TemperhUMMQTTService

def test_config_loading():
    """Test configuration loading"""
    print("Testing TemperhUM MQTT Service configuration loading...")
    
    # Test configuration loading without initializing the full service
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'temperhum_config.json')
    
    print(f"Looking for config file: {config_file}")
    print(f"Config file exists: {os.path.exists(config_file)}")
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"Temperature unit: {config.get('service', {}).get('temperature_unit', 'unknown')}")
        print(f"MQTT host: {config.get('mqtt', {}).get('host', 'unknown')}")
        print(f"HA temperature unit: {config.get('homeassistant', {}).get('unit_temperature', 'unknown')}")
    else:
        print("Config file not found!")

if __name__ == "__main__":
    test_config_loading() 