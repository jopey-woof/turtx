#!/usr/bin/env python3
"""
TemperhUM USB Sensor Controller
Phase 1: Programmatic Sensor Initialization

This module provides Linux-compatible HID control for TemperhUM sensors.
Sensors are HID keyboard devices that can be controlled via keyboard events.
"""

import os
import sys
import time
import logging
import subprocess
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/temperhum_controller.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SensorState:
    """Represents the current state of a TemperhUM sensor"""
    device_path: str
    is_active: bool = False
    interval: int = 0
    last_seen: Optional[float] = None
    banner_received: bool = False

class TemperhUMController:
    """
    Controller for TemperhUM USB sensors using Linux HID input methods.
    
    Supports programmatic control via:
    - evdev for direct device input
    - uinput for kernel-level input injection
    - hidapi for cross-platform HID communication
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.sensors: Dict[str, SensorState] = {}
        self.data_stream_path = "/tmp/temperhum_data.txt"
        self.control_method = None
        self._setup_control_method()
        
    def _setup_control_method(self):
        """Determine the best available HID control method for Linux"""
        methods = [
            ('evdev', self._test_evdev),
            ('uinput', self._test_uinput),
            ('hidapi', self._test_hidapi),
            ('xdotool', self._test_xdotool)
        ]
        
        for method_name, test_func in methods:
            try:
                if test_func():
                    self.control_method = method_name
                    logger.info(f"Using {method_name} for HID control")
                    return
            except Exception as e:
                logger.debug(f"Method {method_name} not available: {e}")
        
        raise RuntimeError("No suitable HID control method found")
    
    def _test_evdev(self) -> bool:
        """Test if evdev is available for direct device input"""
        try:
            import evdev
            # Check if we can access input devices
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            return len(devices) > 0
        except ImportError:
            return False
    
    def _test_uinput(self) -> bool:
        """Test if uinput is available for kernel-level input injection"""
        try:
            import uinput
            return True
        except ImportError:
            return False
    
    def _test_hidapi(self) -> bool:
        """Test if hidapi is available for cross-platform HID communication"""
        try:
            import hid
            return True
        except ImportError:
            return False
    
    def _test_xdotool(self) -> bool:
        """Test if xdotool is available for X11 input simulation"""
        try:
            result = subprocess.run(['which', 'xdotool'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def detect_sensors(self) -> List[str]:
        """
        Detect TemperhUM sensors connected to the system.
        
        Returns:
            List of device paths for detected sensors
        """
        logger.info("🔍 Detecting TemperhUM sensors...")
        
        sensor_paths = []
        temperhum_devices = []
        
        # Method 1: Check /proc/bus/input/devices for TemperhUM devices
        try:
            with open('/proc/bus/input/devices', 'r') as f:
                content = f.read()
                
            # Parse device information
            device_blocks = content.split('\n\n')
            for block in device_blocks:
                if 'TEMPerHUM' in block or 'pcsensor' in block.lower():
                    logger.info(f"Found TemperhUM device block:\n{block}")
                    
                    # Extract event device path
                    for line in block.split('\n'):
                        if line.startswith('H: Handlers='):
                            handlers = line.split('=')[1]
                            if 'event' in handlers:
                                # Extract event number
                                import re
                                event_match = re.search(r'event(\d+)', handlers)
                                if event_match:
                                    event_num = event_match.group(1)
                                    event_path = f"/dev/input/event{event_num}"
                                    sensor_paths.append(event_path)
                                    temperhum_devices.append({
                                        'path': event_path,
                                        'block': block
                                    })
                                    logger.info(f"Added TemperhUM device: {event_path}")
        except Exception as e:
            logger.warning(f"Could not read /proc/bus/input/devices: {e}")
        
        # Method 2: Check USB devices for confirmation
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'pcsensor' in line.lower() or 'temperhum' in line.lower():
                        logger.info(f"Found USB device: {line.strip()}")
        except Exception as e:
            logger.debug(f"Could not run lsusb: {e}")
        
        # Method 3: Check /dev/input/event* devices for accessibility
        accessible_devices = []
        for device_path in sensor_paths:
            try:
                # Test if we can open the device
                with open(device_path, 'rb') as f:
                    accessible_devices.append(device_path)
                    logger.info(f"✅ Accessible device: {device_path}")
            except Exception as e:
                logger.warning(f"❌ Cannot access {device_path}: {e}")
        
        logger.info(f"Detected {len(accessible_devices)} accessible TemperhUM sensor devices")
        return accessible_devices
    
    def send_caps_lock_hold(self, device_path: str, duration: float = 1.0) -> bool:
        """
        Send a Caps Lock hold command to toggle sensor ON/OFF.
        
        Args:
            device_path: Path to the sensor device
            duration: Hold duration in seconds (default 1.0)
            
        Returns:
            True if command was sent successfully
        """
        logger.info(f"🔘 Sending Caps Lock hold ({duration}s) to {device_path}")
        
        try:
            if self.control_method == 'evdev':
                return self._send_caps_lock_evdev(device_path, duration)
            elif self.control_method == 'uinput':
                return self._send_caps_lock_uinput(device_path, duration)
            elif self.control_method == 'xdotool':
                return self._send_caps_lock_xdotool(duration)
            else:
                logger.error(f"Unsupported control method: {self.control_method}")
                return False
        except Exception as e:
            logger.error(f"Failed to send Caps Lock hold: {e}")
            return False
    
    def _send_caps_lock_evdev(self, device_path: str, duration: float) -> bool:
        """Send Caps Lock hold using evdev"""
        try:
            import evdev
            device = evdev.InputDevice(device_path)
            
            # Caps Lock key code is 58
            caps_lock_code = 58
            
            # Send key down
            device.write(evdev.ecodes.EV_KEY, caps_lock_code, 1)
            device.write(evdev.ecodes.EV_SYN, 0, 0)
            
            # Hold for duration
            time.sleep(duration)
            
            # Send key up
            device.write(evdev.ecodes.EV_KEY, caps_lock_code, 0)
            device.write(evdev.ecodes.EV_SYN, 0, 0)
            
            return True
        except Exception as e:
            logger.error(f"evdev Caps Lock failed: {e}")
            return False
    
    def _send_caps_lock_uinput(self, device_path: str, duration: float) -> bool:
        """Send Caps Lock hold using uinput"""
        try:
            import uinput
            
            # Create virtual device
            events = (
                uinput.KEY_CAPSLOCK,
            )
            
            with uinput.Device(events) as device:
                # Send key down
                device.emit(uinput.KEY_CAPSLOCK, 1)
                
                # Hold for duration
                time.sleep(duration)
                
                # Send key up
                device.emit(uinput.KEY_CAPSLOCK, 0)
            
            return True
        except Exception as e:
            logger.error(f"uinput Caps Lock failed: {e}")
            return False
    
    def _send_caps_lock_xdotool(self, duration: float) -> bool:
        """Send Caps Lock hold using xdotool"""
        try:
            # Send key down
            subprocess.run(['xdotool', 'keydown', 'Caps_Lock'], check=True)
            
            # Hold for duration
            time.sleep(duration)
            
            # Send key up
            subprocess.run(['xdotool', 'keyup', 'Caps_Lock'], check=True)
            
            return True
        except Exception as e:
            logger.error(f"xdotool Caps Lock failed: {e}")
            return False
    
    def send_double_press(self, device_path: str, key: str) -> bool:
        """
        Send a double-press command to adjust sensor intervals.
        
        Args:
            device_path: Path to the sensor device
            key: 'caps_lock' to increase interval, 'num_lock' to decrease
            
        Returns:
            True if command was sent successfully
        """
        logger.info(f"🔘 Sending double-press {key} to {device_path}")
        
        try:
            if key == 'caps_lock':
                # Double-press Caps Lock to increase interval
                self.send_caps_lock_hold(device_path, 0.1)
                time.sleep(0.1)
                self.send_caps_lock_hold(device_path, 0.1)
            elif key == 'num_lock':
                # Double-press Num Lock to decrease interval
                if self.control_method == 'xdotool':
                    subprocess.run(['xdotool', 'key', 'Num_Lock'], check=True)
                    time.sleep(0.1)
                    subprocess.run(['xdotool', 'key', 'Num_Lock'], check=True)
                else:
                    # For other methods, we'd need to implement Num Lock
                    logger.warning("Num Lock double-press not implemented for this method")
                    return False
            else:
                logger.error(f"Unknown key: {key}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to send double-press {key}: {e}")
            return False
    
    def initialize_sensor(self, device_path: str) -> bool:
        """
        Initialize a single sensor by toggling it ON and waiting for banner.
        
        Args:
            device_path: Path to the sensor device
            
        Returns:
            True if sensor was successfully initialized
        """
        logger.info(f"🚀 Initializing sensor: {device_path}")
        
        # Create sensor state
        self.sensors[device_path] = SensorState(device_path=device_path)
        
        # Send Caps Lock hold to toggle ON
        if not self.send_caps_lock_hold(device_path):
            logger.error(f"Failed to send Caps Lock hold to {device_path}")
            return False
        
        # Wait for banner output (up to 10 seconds)
        logger.info("⏳ Waiting for sensor banner...")
        start_time = time.time()
        banner_found = False
        
        while time.time() - start_time < 10:
            try:
                # Check if banner appears in any input stream
                if self._check_for_banner():
                    banner_found = True
                    break
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Error checking for banner: {e}")
        
        if banner_found:
            logger.info(f"✅ Sensor {device_path} initialized successfully")
            self.sensors[device_path].is_active = True
            self.sensors[device_path].banner_received = True
            return True
        else:
            logger.warning(f"⚠️ No banner received from {device_path} - sensor may not be active")
            return False
    
    def _check_for_banner(self) -> bool:
        """
        Check for the TemperhUM banner text in input streams.
        
        Returns:
            True if banner text is detected
        """
        banner_indicators = [
            'WWW.PCSENSOR.COM',
            'TEMPERHUM',
            'CAPS LOCK:ON/OFF/++',
            'NUM LOCK:OFF/ON/--'
        ]
        
        # Check /proc/bus/input/devices for recent activity
        try:
            with open('/proc/bus/input/devices', 'r') as f:
                content = f.read()
                if any(indicator in content for indicator in banner_indicators):
                    return True
        except Exception:
            pass
        
        # Check if any keyboard input contains banner text
        # This is a simplified check - in practice we'd monitor actual input
        return False
    
    def initialize_all_sensors(self) -> Dict[str, bool]:
        """
        Initialize all detected TemperhUM sensors.
        
        Returns:
            Dictionary mapping device paths to initialization success status
        """
        logger.info("🚀 Starting sensor initialization sequence...")
        
        # Detect sensors
        sensor_paths = self.detect_sensors()
        
        if not sensor_paths:
            logger.warning("⚠️ No sensors detected")
            return {}
        
        # Initialize each sensor
        results = {}
        for device_path in sensor_paths:
            success = self.initialize_sensor(device_path)
            results[device_path] = success
            
            # Wait between sensors to avoid conflicts
            time.sleep(2)
        
        # Report results
        active_count = sum(1 for success in results.values() if success)
        logger.info(f"✅ Initialization complete: {active_count}/{len(sensor_paths)} sensors active")
        
        return results
    
    def get_sensor_status(self) -> Dict[str, Dict]:
        """
        Get current status of all sensors.
        
        Returns:
            Dictionary with sensor status information
        """
        status = {}
        for device_path, sensor in self.sensors.items():
            status[device_path] = {
                'is_active': sensor.is_active,
                'interval': sensor.interval,
                'banner_received': sensor.banner_received,
                'last_seen': sensor.last_seen
            }
        return status
    
    def test_control_methods(self):
        """Test all available control methods and report results"""
        logger.info("🧪 Testing HID control methods...")
        
        methods = [
            ('evdev', self._test_evdev),
            ('uinput', self._test_uinput),
            ('hidapi', self._test_hidapi),
            ('xdotool', self._test_xdotool)
        ]
        
        results = {}
        for method_name, test_func in methods:
            try:
                available = test_func()
                results[method_name] = available
                status = "✅ Available" if available else "❌ Not available"
                logger.info(f"{method_name}: {status}")
            except Exception as e:
                results[method_name] = False
                logger.info(f"{method_name}: ❌ Error - {e}")
        
        return results

def main():
    """Main function for testing sensor initialization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TemperhUM Sensor Controller - Phase 1')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--test-methods', action='store_true', help='Test available control methods')
    parser.add_argument('--init-sensors', action='store_true', help='Initialize all detected sensors')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    controller = TemperhUMController(debug=args.debug)
    
    if args.test_methods:
        controller.test_control_methods()
    
    if args.init_sensors:
        results = controller.initialize_all_sensors()
        print("\n📊 Initialization Results:")
        for device_path, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {device_path}: {status}")
        
        print("\n📈 Sensor Status:")
        status = controller.get_sensor_status()
        for device_path, info in status.items():
            print(f"  {device_path}:")
            print(f"    Active: {info['is_active']}")
            print(f"    Banner: {info['banner_received']}")
            print(f"    Interval: {info['interval']}")

if __name__ == "__main__":
    main() 