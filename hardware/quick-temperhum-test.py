#!/usr/bin/env python3
"""
Quick TEMPerHUM Test Script
===========================

A simplified script for quick TEMPerHUM sensor validation.
This script performs basic checks without the full interactive process.

Usage:
    python3 quick-temperhum-test.py
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_cmd(cmd):
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def check_python():
    """Check Python version."""
    print("✓ Python version:", sys.version.split()[0])
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")
    
    # Check temper-py
    try:
        import temper
        print("✓ temper-py installed")
        return True
    except ImportError:
        print("✗ temper-py not installed")
        print("  Install with: pip3 install temper-py")
        return False

def check_usb_devices():
    """Check for TEMPerHUM USB devices."""
    print("\nChecking USB devices...")
    
    output, code = run_cmd("lsusb")
    if code != 0:
        print("✗ Failed to run lsusb")
        return False
    
    temperhum_ids = ["413d:2107", "1a86:e025", "3553:a001", "0c45:7401", "0c45:7402"]
    found = []
    
    for line in output.split('\n'):
        if any(id_pair in line for id_pair in temperhum_ids):
            found.append(line.strip())
            print(f"✓ TEMPerHUM detected: {line.strip()}")
    
    if not found:
        print("✗ No TEMPerHUM sensors found")
        print("  Make sure sensors are plugged in")
        return False
    
    return True

def test_temper_py():
    """Test temper-py functionality."""
    print("\nTesting temper-py...")
    
    commands = ["temper.py", "python3 -m temper"]
    
    for cmd in commands:
        output, code = run_cmd(cmd)
        if code == 0 and output:
            print(f"✓ {cmd} working")
            print(f"  Output: {output[:100]}...")
            return True
    
    print("✗ temper-py not working")
    return False

def quick_manual_test():
    """Quick manual test with user input."""
    print("\nQuick manual test...")
    print("Press TXT button on sensor or hold Caps Lock for 3 seconds")
    print("Type the output you see (or 'skip' to skip):")
    
    try:
        user_input = input("Sensor output: ").strip()
        if user_input.lower() == 'skip':
            return None
        
        # Simple parsing
        if '°C' in user_input or 'C' in user_input:
            print("✓ Manual test successful")
            return user_input
        else:
            print("✗ Invalid sensor output format")
            return None
    except KeyboardInterrupt:
        return None

def main():
    """Main test function."""
    print("TEMPerHUM Quick Test")
    print("===================")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test 1: Python
    results['tests']['python'] = check_python()
    
    # Test 2: Dependencies
    results['tests']['dependencies'] = check_dependencies()
    
    # Test 3: USB Devices
    results['tests']['usb_devices'] = check_usb_devices()
    
    # Test 4: temper-py
    if results['tests']['dependencies']:
        results['tests']['temper_py'] = test_temper_py()
    else:
        results['tests']['temper_py'] = False
    
    # Test 5: Manual test
    if results['tests']['usb_devices']:
        manual_result = quick_manual_test()
        results['tests']['manual_test'] = manual_result is not None
        if manual_result:
            results['manual_output'] = manual_result
    else:
        results['tests']['manual_test'] = False
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results['tests'])
    
    for test, result in results['tests'].items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/tmp/temperhum_quick_test_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {filename}")
    
    if passed == total:
        print("\n🎉 All tests passed! Sensors are working correctly.")
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1) 