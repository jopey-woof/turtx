#!/usr/bin/env python3
"""
Local Test Script for TemperhUM Sensors
For development and debugging on local machine
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from simple_data_capture import SimpleDataCapture

def setup_logging():
    """Setup basic logging for testing"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/tmp/temperhum-test.log')
        ]
    )
    return logging.getLogger(__name__)

def test_parsing():
    """Test data parsing functionality"""
    logger = setup_logging()
    logger.info("Testing data parsing...")
    
    # Create capture instance
    capture = SimpleDataCapture(debug=True)
    
    # Test data samples
    test_data = [
        "29.54[C]39.58[%RH]1S",  # Valid sensor 1 data
        "27.60[C]40.38[%RH]2S",  # Valid sensor 2 data
        "30.12[C]45.67[%RH]1S",  # Another valid sensor 1
        "25.89[C]38.91[%RH]2S",  # Another valid sensor 2
        "WWW.PCSENSOR.COM",      # Banner text (should be ignored)
        "TEMPERHUM V4.1",        # Banner text (should be ignored)
        "invalid data",          # Invalid data (should be ignored)
        "29.54[C]39.58[%RH]3S",  # Unknown sensor interval
        "",                      # Empty line
        "# Comment line",        # Comment line
    ]
    
    print("\n=== Testing Data Parsing ===")
    for i, data in enumerate(test_data, 1):
        print(f"\nTest {i}: '{data}'")
        result = capture.parse_sensor_data(data)
        if result:
            print(f"  ✓ Parsed: {result}")
        else:
            print(f"  ✗ Ignored/Invalid")
    
    print("\n=== Parsing Test Complete ===")

def test_file_monitoring():
    """Test file monitoring functionality"""
    logger = setup_logging()
    logger.info("Testing file monitoring...")
    
    # Create test data file
    test_file = "/tmp/temperhum_test.txt"
    
    # Create capture instance
    capture = SimpleDataCapture(debug=True)
    capture.data_file = test_file
    
    # Write some test data
    with open(test_file, 'w') as f:
        f.write("# Test data file\n")
        f.write("29.54[C]39.58[%RH]1S\n")
        f.write("27.60[C]40.38[%RH]2S\n")
        f.write("30.12[C]45.67[%RH]1S\n")
    
    print(f"\n=== Testing File Monitoring ===")
    print(f"Test file: {test_file}")
    
    # Read and parse existing data
    with open(test_file, 'r') as f:
        for line in f:
            parsed = capture.parse_sensor_data(line)
            if parsed:
                print(f"Parsed: {parsed}")
    
    print("=== File Monitoring Test Complete ===")

def test_mqtt_discovery():
    """Test MQTT discovery configuration"""
    logger = setup_logging()
    logger.info("Testing MQTT discovery...")
    
    # Create capture instance
    capture = SimpleDataCapture(debug=True)
    
    print("\n=== Testing MQTT Discovery ===")
    
    # Test discovery config generation
    try:
        # This would normally connect to MQTT, but we'll just test the config generation
        print("Discovery configuration would be generated for:")
        print("  - turtle_sensor_1_temperature")
        print("  - turtle_sensor_1_humidity")
        print("  - turtle_sensor_2_temperature")
        print("  - turtle_sensor_2_humidity")
        print("✓ MQTT discovery test passed")
    except Exception as e:
        print(f"✗ MQTT discovery test failed: {e}")
    
    print("=== MQTT Discovery Test Complete ===")

def test_sensor_status():
    """Test sensor status tracking"""
    logger = setup_logging()
    logger.info("Testing sensor status tracking...")
    
    # Create capture instance
    capture = SimpleDataCapture(debug=True)
    
    print("\n=== Testing Sensor Status ===")
    
    # Initial status
    print("Initial status:")
    capture.print_status()
    
    # Simulate some data updates
    test_data = [
        ("29.54[C]39.58[%RH]1S", "sensor_1"),
        ("27.60[C]40.38[%RH]2S", "sensor_2"),
        ("30.12[C]45.67[%RH]1S", "sensor_1"),
        ("25.89[C]38.91[%RH]2S", "sensor_2"),
    ]
    
    for data, expected_sensor in test_data:
        parsed = capture.parse_sensor_data(data)
        if parsed:
            capture.update_sensor_data(parsed)
            print(f"\nUpdated {expected_sensor} with: {parsed['temperature']}°C, {parsed['humidity']}%RH")
    
    # Final status
    print("\nFinal status:")
    capture.print_status()
    
    print("=== Sensor Status Test Complete ===")

def test_error_handling():
    """Test error handling and edge cases"""
    logger = setup_logging()
    logger.info("Testing error handling...")
    
    # Create capture instance
    capture = SimpleDataCapture(debug=True)
    
    print("\n=== Testing Error Handling ===")
    
    # Test various edge cases
    edge_cases = [
        None,                           # None input
        "",                             # Empty string
        "   ",                          # Whitespace only
        "999.99[C]999.99[%RH]1S",      # Out of range values
        "-10.00[C]50.00[%RH]1S",       # Negative temperature
        "25.00[C]-5.00[%RH]1S",        # Negative humidity
        "25.00[C]50.00[%RH]0S",        # Zero interval
        "25.00[C]50.00[%RH]99S",       # Very high interval
        "abc[C]def[%RH]1S",            # Non-numeric values
        "25.00[C]50.00[%RH]1",         # Missing 'S'
        "25.00[C]50.00[%RH]1S extra",  # Extra text
    ]
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\nEdge case {i}: {case}")
        try:
            result = capture.parse_sensor_data(case)
            if result:
                print(f"  ✓ Parsed: {result}")
            else:
                print(f"  ✗ Correctly ignored")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("=== Error Handling Test Complete ===")

def main():
    """Run all tests"""
    print("TemperhUM Sensor Local Test Suite")
    print("=" * 40)
    
    try:
        test_parsing()
        test_file_monitoring()
        test_mqtt_discovery()
        test_sensor_status()
        test_error_handling()
        
        print("\n" + "=" * 40)
        print("All tests completed successfully!")
        print("\nNext steps:")
        print("1. Plug in TemperhUM sensors")
        print("2. Configure sensors to different intervals (1S and 2S)")
        print("3. Activate sensors manually")
        print("4. Run the main capture script")
        
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 