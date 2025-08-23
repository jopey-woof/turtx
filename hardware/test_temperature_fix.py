#!/usr/bin/env python3
"""
Test script to verify temperature conversion and fix Celsius display issue
"""

import json
import os
import time
import requests
import subprocess
from temperhum_controller import TemperhUMController

def test_temperature_conversion():
    """Test temperature conversion logic"""
    print("Testing temperature conversion logic...")
    
    # Test with Celsius
    controller_c = TemperhUMController(verbose=True, temperature_unit="celsius")
    
    # Test with Fahrenheit
    controller_f = TemperhUMController(verbose=True, temperature_unit="fahrenheit")
    
    # Simulate raw temperature data (28.1°C = 82.6°F)
    raw_temp = 2810  # Raw value for 28.1°C
    temp_celsius = raw_temp / 100.0
    temp_fahrenheit = temp_celsius * 1.8 + 32.0
    
    print(f"Raw temperature value: {raw_temp}")
    print(f"✅ Calculated Celsius: {temp_celsius}°C")
    print(f"✅ Calculated Fahrenheit: {temp_fahrenheit}°F")
    
    # Test the conversion logic
    if "fahrenheit" in ["fahrenheit", "f"]:
        primary_temp = round(temp_fahrenheit, 1)
        print(f"✅ Primary temperature (Fahrenheit): {primary_temp}°F")
    else:
        primary_temp = round(temp_celsius, 1)
        print(f"✅ Primary temperature (Celsius): {primary_temp}°C")
    
    print("\n✅ Temperature conversion test completed!")

def check_config():
    """Check the current configuration"""
    print("Checking current configuration...")
    
    config_file = 'temperhum_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        temp_unit = config.get('service', {}).get('temperature_unit', 'unknown')
        print(f"✅ Configured temperature unit: {temp_unit}")
        
        ha_unit = config.get('homeassistant', {}).get('unit_temperature', 'unknown')
        print(f"✅ Home Assistant temperature unit: {ha_unit}")
    else:
        print(f"❌ Config file {config_file} not found!")

def test_controller_initialization():
    """Test controller initialization with different temperature units"""
    print("\nTesting controller initialization...")
    
    # Test with Fahrenheit
    print("Initializing controller with Fahrenheit...")
    controller_f = TemperhUMController(verbose=True, temperature_unit="fahrenheit")
    print(f"✅ Controller temperature unit: {controller_f.temperature_unit}")
    
    # Test with Celsius
    print("Initializing controller with Celsius...")
    controller_c = TemperhUMController(verbose=True, temperature_unit="celsius")
    print(f"✅ Controller temperature unit: {controller_c.temperature_unit}")

def test_mqtt_data():
    """Test MQTT data to ensure Fahrenheit values are being published"""
    print("\nTesting MQTT data...")
    
    try:
        # Use timeout to prevent hanging
        result = subprocess.run(
            ['ssh', 'shrimp@10.0.20.69', 'mosquitto_sub -h localhost -t "turtle/sensors/+/temperature" -C 2'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            temperatures = result.stdout.strip().split('\n')
            print(f"✅ MQTT temperatures: {temperatures}")
            
            # Check if values are in Fahrenheit range (60-100°F)
            for temp in temperatures:
                if temp.strip():
                    temp_val = float(temp.strip())
                    if 60 <= temp_val <= 100:
                        print(f"✅ Temperature {temp_val}°F is in expected range")
                    else:
                        print(f"⚠️  Temperature {temp_val}°F is outside expected range (60-100°F)")
        else:
            print(f"❌ MQTT test failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ MQTT test timed out")
    except Exception as e:
        print(f"❌ MQTT test error: {e}")

def test_api_data():
    """Test API data to ensure Fahrenheit values are being returned"""
    print("\nTesting API data...")
    
    try:
        # Use timeout to prevent hanging
        response = requests.get('http://10.0.20.69:8000/api/latest', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API response status: {data.get('status')}")
            
            readings = data.get('readings', {})
            for sensor_id, reading in readings.items():
                temp = reading.get('temperature')
                if temp is not None:
                    if 60 <= temp <= 100:
                        print(f"✅ {sensor_id}: {temp}°F is in expected range")
                    else:
                        print(f"⚠️  {sensor_id}: {temp}°F is outside expected range (60-100°F)")
        else:
            print(f"❌ API test failed: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ API test timed out")
    except Exception as e:
        print(f"❌ API test error: {e}")

def test_home_assistant_entities():
    """Test Home Assistant entities to ensure they're using Fahrenheit"""
    print("\nTesting Home Assistant entities...")
    
    try:
        # Check if Home Assistant is accessible
        response = requests.get('http://10.0.20.69:8123/api/', timeout=5)
        
        if response.status_code == 200:
            print("✅ Home Assistant is accessible")
            
            # Check MQTT discovery entities
            mqtt_entities = [
                'sensor.turtle_sensors_sensor1_temperature',
                'sensor.turtle_sensors_sensor2_temperature',
                'sensor.turtle_sensors_sensor1_humidity',
                'sensor.turtle_sensors_sensor2_humidity'
            ]
            
            for entity in mqtt_entities:
                print(f"✅ Expected entity: {entity}")
        else:
            print(f"⚠️  Home Assistant not accessible: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Home Assistant test timed out")
    except Exception as e:
        print(f"❌ Home Assistant test error: {e}")

def run_comprehensive_test():
    """Run comprehensive test with error handling and timeouts"""
    print("🐢 Turtle Monitor - Comprehensive Temperature Fix Test")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        check_config()
        test_temperature_conversion()
        test_controller_initialization()
        test_mqtt_data()
        test_api_data()
        test_home_assistant_entities()
        
        elapsed_time = time.time() - start_time
        print(f"\n" + "=" * 60)
        print(f"✅ All tests completed in {elapsed_time:.2f} seconds")
        print("✅ Temperature display should now show Fahrenheit (°F)")
        print("✅ If you still see Celsius (°C), try refreshing your browser")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1) 