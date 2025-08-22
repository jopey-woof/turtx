#!/usr/bin/env python3
"""
TEMPerHUM USB Sensor Installer and Tester
==========================================

This script provides an interactive, attended process for installing and testing
TEMPerHUM USB temperature/humidity sensors on a remote Linux machine.

Features:
- Interactive step-by-step guidance
- Automatic dependency installation
- Device detection and enumeration
- Programmatic reading via temper-py
- Fallback to manual activation mode
- Comprehensive error handling and debugging

Usage:
    python3 temperhum_test_installer.py

Requirements:
    - Python 3.6+
    - SSH access to remote machine
    - TEMPerHUM USB sensors (vendor IDs: 413d:2107, 1a86:e025, etc.)
"""

import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ANSI color codes for better output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_step(text: str):
    """Print a step instruction."""
    print(f"{Colors.OKBLUE}{Colors.BOLD}→ {text}{Colors.ENDC}")

def print_success(text: str):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def run_command(cmd: str, capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        else:
            result = subprocess.run(cmd, shell=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        return e

def check_python_version():
    """Check if Python version is compatible."""
    print_step("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print_error(f"Python 3.6+ required. Found: {version.major}.{version.minor}")
        sys.exit(1)
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")

def install_dependencies():
    """Install required system and Python dependencies."""
    print_step("Installing system dependencies...")
    
    # Update package list
    print_info("Updating package list...")
    run_command("sudo apt update", capture_output=False)
    
    # Install system packages
    packages = [
        "python3-pip",
        "python3-serial",
        "python3-dev",
        "build-essential",
        "libusb-1.0-0-dev",
        "mosquitto-clients"
    ]
    
    for package in packages:
        print_info(f"Installing {package}...")
        result = run_command(f"sudo apt install -y {package}", check=False)
        if result.returncode != 0:
            print_warning(f"Failed to install {package}, continuing...")
    
    print_step("Installing Python packages...")
    
    # Install temper-py
    print_info("Installing temper-py...")
    result = run_command("pip3 install temper-py", check=False)
    if result.returncode != 0:
        print_warning("Failed to install temper-py via pip, trying alternative...")
        result = run_command("python3 -m pip install temper-py", check=False)
        if result.returncode != 0:
            print_error("Failed to install temper-py. Please install manually:")
            print_info("pip3 install temper-py")
            return False
    
    print_success("Dependencies installed successfully")
    return True

def detect_usb_devices() -> List[Dict]:
    """Detect and list USB devices, focusing on TEMPerHUM sensors."""
    print_step("Detecting USB devices...")
    
    # Get all USB devices
    result = run_command("lsusb")
    if result.returncode != 0:
        print_error("Failed to run lsusb")
        return []
    
    devices = []
    lines = result.stdout.strip().split('\n')
    
    # Known TEMPerHUM vendor/product IDs
    temperhum_ids = [
        "413d:2107",  # TEMPerHUM
        "1a86:e025",  # TEMPerHUM
        "3553:a001",  # TEMPerHUM
        "0c45:7401",  # TEMPerHUM
        "0c45:7402",  # TEMPerHUM
    ]
    
    for line in lines:
        if any(id_pair in line for id_pair in temperhum_ids):
            devices.append({
                'line': line.strip(),
                'vendor_product': next(id_pair for id_pair in temperhum_ids if id_pair in line)
            })
            print_success(f"TEMPerHUM sensor detected: {line.strip()}")
    
    if not devices:
        print_warning("No TEMPerHUM sensors detected via lsusb")
        print_info("This is normal if sensors are not plugged in yet")
    
    return devices

def detect_hid_devices() -> List[Dict]:
    """Detect HID devices that might be TEMPerHUM sensors."""
    print_step("Detecting HID devices...")
    
    try:
        # Check if /sys/class/hidraw exists
        if not os.path.exists('/sys/class/hidraw'):
            print_warning("HIDRAW devices not available")
            return []
        
        devices = []
        hidraw_path = '/sys/class/hidraw'
        
        for device_dir in os.listdir(hidraw_path):
            device_path = os.path.join(hidraw_path, device_dir)
            uevent_path = os.path.join(device_path, 'device', 'uevent')
            
            if os.path.exists(uevent_path):
                with open(uevent_path, 'r') as f:
                    uevent_data = f.read()
                
                # Look for TEMPerHUM identifiers
                if any(id_pair in uevent_data for id_pair in ["413d:2107", "1a86:e025", "3553:a001"]):
                    device_info = {
                        'hidraw': f"/dev/{device_dir}",
                        'uevent': uevent_data,
                        'path': device_path
                    }
                    devices.append(device_info)
                    print_success(f"HID device detected: {device_dir}")
        
        return devices
    
    except Exception as e:
        print_warning(f"Error detecting HID devices: {e}")
        return []

def test_temper_py():
    """Test temper-py installation and basic functionality."""
    print_step("Testing temper-py installation...")
    
    # Test import
    try:
        import temper
        print_success("temper-py imported successfully")
    except ImportError as e:
        print_error(f"Failed to import temper-py: {e}")
        return False
    
    # Test CLI
    print_info("Testing temper-py CLI...")
    result = run_command("temper.py --help", check=False)
    if result.returncode == 0:
        print_success("temper-py CLI working")
        return True
    else:
        print_warning("temper-py CLI not working, trying alternative...")
        result = run_command("python3 -m temper --help", check=False)
        if result.returncode == 0:
            print_success("temper-py module working")
            return True
        else:
            print_error("temper-py not working properly")
            return False

def read_sensor_temper_py(sensor_id: int) -> Optional[Dict]:
    """Read sensor data using temper-py."""
    print_step(f"Reading sensor {sensor_id} via temper-py...")
    
    # Try different temper-py commands
    commands = [
        "temper.py",
        "python3 -m temper",
        "temper.py --list",
        "python3 -m temper --list"
    ]
    
    for cmd in commands:
        try:
            result = run_command(cmd, check=False)
            if result.returncode == 0 and result.stdout.strip():
                print_success(f"temper-py output: {result.stdout.strip()}")
                
                # Parse the output (format varies by version)
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '°C' in line or '°F' in line or '%' in line:
                        return {
                            'sensor_id': sensor_id,
                            'method': 'temper-py',
                            'raw_output': line.strip(),
                            'timestamp': datetime.now().isoformat()
                        }
        except Exception as e:
            print_warning(f"Command {cmd} failed: {e}")
    
    return None

def setup_manual_capture():
    """Set up manual capture mode for button-activated sensors."""
    print_step("Setting up manual capture mode...")
    
    # Create capture script
    capture_script = '''#!/usr/bin/env python3
import sys
import time
from datetime import datetime

print("Manual capture mode active. Press TXT button or hold Caps Lock for 3 seconds...")
print("Type 'quit' to exit")

captured_data = []

try:
    while True:
        line = input()
        if line.lower() == 'quit':
            break
        
        timestamp = datetime.now().isoformat()
        captured_data.append({
            'timestamp': timestamp,
            'raw_data': line.strip()
        })
        print(f"Captured: {line.strip()}")
        
except KeyboardInterrupt:
    pass

# Save captured data
with open('/tmp/temperhum_captured_data.json', 'w') as f:
    json.dump(captured_data, f, indent=2)

print(f"Captured {len(captured_data)} readings")
'''
    
    with open('/tmp/temperhum_capture.py', 'w') as f:
        f.write(capture_script)
    
    run_command("chmod +x /tmp/temperhum_capture.py")
    print_success("Manual capture script created")

def parse_manual_data(raw_data: str) -> Optional[Dict]:
    """Parse manually captured sensor data."""
    # Common TEMPerHUM output formats
    patterns = [
        # Format: "32.73[C]36.82[%RH]1S"
        r'(\d+\.?\d*)\[C\](\d+\.?\d*)\[%RH\](\d+)S',
        # Format: "32.73°C 36.82%"
        r'(\d+\.?\d*)°C\s+(\d+\.?\d*)%',
        # Format: "Temp: 32.73°C, Humidity: 36.82%"
        r'Temp:\s*(\d+\.?\d*)°C.*Humidity:\s*(\d+\.?\d*)%',
    ]
    
    import re
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

def test_sensor_manual(sensor_id: int) -> Optional[Dict]:
    """Test sensor using manual activation mode."""
    print_step(f"Testing sensor {sensor_id} in manual mode...")
    
    print_info("Instructions:")
    print_info("1. Ensure sensor is plugged in")
    print_info("2. Press the TXT button on the sensor")
    print_info("3. Or hold Caps Lock for 3 seconds")
    print_info("4. Watch for typed output")
    
    input("Press Enter when ready to capture data...")
    
    # Start capture in background
    print_info("Starting capture (will run for 30 seconds)...")
    capture_process = subprocess.Popen(
        ["python3", "/tmp/temperhum_capture.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for capture
        time.sleep(30)
        capture_process.terminate()
        capture_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        capture_process.kill()
    
    # Check for captured data
    if os.path.exists('/tmp/temperhum_captured_data.json'):
        with open('/tmp/temperhum_captured_data.json', 'r') as f:
            captured_data = json.load(f)
        
        if captured_data:
            print_success(f"Captured {len(captured_data)} readings")
            
            # Parse the first valid reading
            for reading in captured_data:
                parsed = parse_manual_data(reading['raw_data'])
                if parsed:
                    return {
                        'sensor_id': sensor_id,
                        'method': 'manual',
                        'temperature': parsed['temperature'],
                        'humidity': parsed['humidity'],
                        'raw_data': parsed['raw_data'],
                        'timestamp': reading['timestamp']
                    }
    
    print_warning("No valid sensor data captured")
    return None

def test_sensor_interactive(sensor_id: int) -> Optional[Dict]:
    """Interactive sensor testing with user guidance."""
    print_header(f"Testing Sensor {sensor_id}")
    
    print_info(f"Testing sensor {sensor_id} - Interactive Mode")
    print_info("This will guide you through testing the sensor step by step")
    
    # Step 1: Check if sensor is plugged in
    print_step("Step 1: Verify sensor connection")
    input(f"Please ensure sensor {sensor_id} is plugged into a USB port, then press Enter...")
    
    # Step 2: Detect device
    print_step("Step 2: Detecting sensor...")
    usb_devices = detect_usb_devices()
    hid_devices = detect_hid_devices()
    
    if not usb_devices and not hid_devices:
        print_warning("No TEMPerHUM sensors detected")
        print_info("Please check:")
        print_info("- Sensor is properly plugged in")
        print_info("- USB port is working")
        print_info("- Sensor is not in a special mode")
        input("Press Enter to continue anyway...")
    
    # Step 3: Try programmatic reading
    print_step("Step 3: Attempting programmatic reading...")
    result = read_sensor_temper_py(sensor_id)
    
    if result:
        print_success("Programmatic reading successful!")
        print_info(f"Raw output: {result['raw_output']}")
        return result
    
    # Step 4: Fallback to manual mode
    print_step("Step 4: Programmatic reading failed, trying manual mode...")
    setup_manual_capture()
    
    result = test_sensor_manual(sensor_id)
    if result:
        print_success("Manual reading successful!")
        return result
    
    # Step 5: Final troubleshooting
    print_step("Step 5: Troubleshooting...")
    print_warning("Sensor testing failed. Please check:")
    print_info("1. Sensor is properly connected")
    print_info("2. Try a different USB port")
    print_info("3. Check if sensor LED is on")
    print_info("4. Try pressing TXT button to activate")
    print_info("5. Check system logs: dmesg | tail -20")
    
    return None

def save_test_results(results: List[Dict]):
    """Save test results to a file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"/tmp/temperhum_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print_success(f"Test results saved to {filename}")

def main():
    """Main function for the TEMPerHUM installer and tester."""
    print_header("TEMPerHUM USB Sensor Installer and Tester")
    
    print_info("This script will guide you through installing and testing TEMPerHUM sensors")
    print_info("Make sure you have SSH access to the remote machine")
    print_info("Have your TEMPerHUM sensors ready")
    
    input("Press Enter to continue...")
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    print_header("Installing Dependencies")
    if not install_dependencies():
        print_error("Failed to install dependencies")
        sys.exit(1)
    
    # Test temper-py
    if not test_temper_py():
        print_warning("temper-py not working properly, will use manual mode")
    
    # Initial device detection
    print_header("Initial Device Detection")
    usb_devices = detect_usb_devices()
    hid_devices = detect_hid_devices()
    
    print_info(f"Found {len(usb_devices)} USB devices and {len(hid_devices)} HID devices")
    
    # Test sensors
    print_header("Sensor Testing")
    results = []
    
    for sensor_id in [1, 2]:
        print_info(f"\nTesting sensor {sensor_id}...")
        result = test_sensor_interactive(sensor_id)
        
        if result:
            results.append(result)
            print_success(f"Sensor {sensor_id} test successful!")
            print_info(f"Temperature: {result.get('temperature', 'N/A')}°C")
            print_info(f"Humidity: {result.get('humidity', 'N/A')}%")
        else:
            print_warning(f"Sensor {sensor_id} test failed")
        
        if sensor_id == 1:
            input("Press Enter to continue to sensor 2...")
    
    # Summary
    print_header("Test Summary")
    if results:
        print_success(f"Successfully tested {len(results)} sensors")
        for result in results:
            print_info(f"Sensor {result['sensor_id']}: {result['method']} method")
            if 'temperature' in result:
                print_info(f"  Temperature: {result['temperature']}°C")
            if 'humidity' in result:
                print_info(f"  Humidity: {result['humidity']}%")
        
        save_test_results(results)
    else:
        print_error("No sensors were successfully tested")
        print_info("Please check your connections and try again")
    
    # Next steps
    print_header("Next Steps")
    print_info("If sensors are working, you can:")
    print_info("1. Integrate with Home Assistant")
    print_info("2. Set up automated monitoring")
    print_info("3. Configure alerts and notifications")
    print_info("4. View test results in /tmp/temperhum_test_results_*.json")
    
    print_success("TEMPerHUM testing complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\nTesting interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1) 