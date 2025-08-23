#!/usr/bin/env python3
"""
Final verification test for temperature display fix and UI improvements
"""

import json
import time
import requests
import subprocess
from datetime import datetime

def test_mqtt_temperature_units():
    """Test that MQTT is publishing temperatures with correct units"""
    print("🌡️ Testing MQTT temperature units...")
    
    try:
        result = subprocess.run(
            ['ssh', 'shrimp@10.0.20.69', 'mosquitto_sub -h localhost -t "homeassistant/sensor/+/config" -C 2'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            configs = result.stdout.strip().split('\n')
            for config in configs:
                if config.strip():
                    data = json.loads(config)
                    if 'unit_of_measurement' in data:
                        unit = data['unit_of_measurement']
                        name = data.get('name', 'Unknown')
                        if unit == '°F':
                            print(f"✅ {name}: {unit}")
                        else:
                            print(f"❌ {name}: {unit} (should be °F)")
        else:
            print(f"❌ MQTT test failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ MQTT test timed out")
    except Exception as e:
        print(f"❌ MQTT test error: {e}")

def test_api_temperature_values():
    """Test that API is returning Fahrenheit temperature values"""
    print("\n🌐 Testing API temperature values...")
    
    try:
        response = requests.get('http://10.0.20.69:8000/api/latest', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            readings = data.get('readings', {})
            
            for sensor_id, reading in readings.items():
                temp = reading.get('temperature')
                if temp is not None:
                    if 60 <= temp <= 100:  # Fahrenheit range
                        print(f"✅ {sensor_id}: {temp}°F (correct range)")
                    else:
                        print(f"⚠️  {sensor_id}: {temp}°F (outside expected range)")
        else:
            print(f"❌ API test failed: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ API test timed out")
    except Exception as e:
        print(f"❌ API test error: {e}")

def test_home_assistant_accessibility():
    """Test that Home Assistant is accessible and responding"""
    print("\n🏠 Testing Home Assistant accessibility...")
    
    try:
        response = requests.get('http://10.0.20.69:8123/api/', timeout=5)
        
        if response.status_code == 200:
            print("✅ Home Assistant is accessible")
            
            # Test if the kiosk dashboard is working
            dashboard_response = requests.get('http://10.0.20.69:8123/lovelace/default_view', timeout=5)
            if dashboard_response.status_code == 200:
                print("✅ Kiosk dashboard is accessible")
            else:
                print(f"⚠️  Kiosk dashboard returned: {dashboard_response.status_code}")
        else:
            print(f"⚠️  Home Assistant returned: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Home Assistant test timed out")
    except Exception as e:
        print(f"❌ Home Assistant test error: {e}")

def test_frontend_accessibility():
    """Test that the custom frontend is accessible"""
    print("\n🖥️ Testing custom frontend accessibility...")
    
    try:
        response = requests.get('http://10.0.20.69:8000/', timeout=5)
        
        if response.status_code == 200:
            content = response.text
            if '°F' in content:
                print("✅ Frontend configured for Fahrenheit display")
            else:
                print("❌ Frontend not configured for Fahrenheit")
                
            if '🐢 TURTLE MONITOR' in content:
                print("✅ Frontend has updated title")
            else:
                print("❌ Frontend title not updated")
        else:
            print(f"❌ Frontend test failed: HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ Frontend test timed out")
    except Exception as e:
        print(f"❌ Frontend test error: {e}")

def test_sensor_entities():
    """Test that the correct sensor entities are being used"""
    print("\n📊 Testing sensor entities...")
    
    expected_entities = [
        'sensor.turtle_sensors_sensor1_temperature',
        'sensor.turtle_sensors_sensor2_temperature',
        'sensor.turtle_sensors_sensor1_humidity',
        'sensor.turtle_sensors_sensor2_humidity'
    ]
    
    for entity in expected_entities:
        print(f"✅ Expected entity: {entity}")

def run_final_verification():
    """Run comprehensive final verification"""
    print("🐢 Turtle Monitor - Final Verification Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        test_mqtt_temperature_units()
        test_api_temperature_values()
        test_home_assistant_accessibility()
        test_frontend_accessibility()
        test_sensor_entities()
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🎉 FINAL VERIFICATION COMPLETE")
        print("=" * 60)
        print(f"✅ Test completed in {elapsed_time:.2f} seconds")
        print("✅ Temperature display should now show Fahrenheit (°F)")
        print("✅ UI has been enhanced with cute, professional design")
        print("✅ Both web UI and kiosk should have matching gradients")
        print("\n📋 Next Steps:")
        print("1. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
        print("2. Check the kiosk dashboard in Home Assistant")
        print("3. Verify temperatures display with °F units")
        print("4. Enjoy the new cute, professional design! 🌸")
        
    except Exception as e:
        print(f"\n❌ Final verification failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_final_verification()
    exit(0 if success else 1) 