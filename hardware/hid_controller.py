#!/usr/bin/env python3
"""
Linux HID Controller for TemperhUM Sensors
Handles programmatic control of HID keyboard devices
"""

import os
import time
import logging
import subprocess
import struct
from typing import List, Dict, Optional
import evdev
from evdev import ecodes, InputEvent, InputDevice

class HIDController:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.devices = []
        self.virtual_device = None
        
    def find_temperhum_devices(self) -> List[Dict]:
        """Find TemperhUM HID devices"""
        devices = []
        
        try:
            for device_path in evdev.list_devices():
                try:
                    device = InputDevice(device_path)
                    
                    # Check if it's a keyboard device
                    if ecodes.EV_KEY in device.capabilities():
                        # Look for TemperhUM characteristics
                        device_info = {
                            'path': device_path,
                            'name': device.name,
                            'phys': device.phys,
                            'device': device,
                            'vendor_id': None,
                            'product_id': None
                        }
                        
                        # Try to get USB info
                        try:
                            # Read device info from sysfs
                            usb_path = f"/sys/class/input/{os.path.basename(device_path)}/device"
                            if os.path.exists(usb_path):
                                vendor_file = os.path.join(usb_path, "idVendor")
                                product_file = os.path.join(usb_path, "idProduct")
                                
                                if os.path.exists(vendor_file):
                                    with open(vendor_file, 'r') as f:
                                        device_info['vendor_id'] = f.read().strip()
                                
                                if os.path.exists(product_file):
                                    with open(product_file, 'r') as f:
                                        device_info['product_id'] = f.read().strip()
                        except Exception as e:
                            self.logger.debug(f"Could not read USB info: {e}")
                        
                        devices.append(device_info)
                        self.logger.info(f"Found HID device: {device.name} at {device_path}")
                        
                except Exception as e:
                    self.logger.debug(f"Error reading device {device_path}: {e}")
                    continue
            
            self.logger.info(f"Found {len(devices)} potential HID devices")
            return devices
            
        except Exception as e:
            self.logger.error(f"Error finding HID devices: {e}")
            return []
    
    def create_virtual_device(self):
        """Create a virtual input device for sending commands"""
        try:
            # Check if uinput module is loaded
            result = subprocess.run(['modprobe', 'uinput'], capture_output=True)
            if result.returncode != 0:
                self.logger.warning("Could not load uinput module")
                return False
            
            # Check if /dev/uinput exists and is writable
            if not os.path.exists('/dev/uinput'):
                self.logger.error("/dev/uinput does not exist")
                return False
            
            # Create virtual device using uinput
            # This is a simplified approach - in production we'd need proper uinput setup
            self.logger.info("Virtual device creation not fully implemented")
            return False
            
        except Exception as e:
            self.logger.error(f"Error creating virtual device: {e}")
            return False
    
    def send_key_event(self, device_path: str, key_code: int, press: bool = True):
        """Send a key event to a specific device"""
        try:
            device = InputDevice(device_path)
            
            # Create input event
            event = InputEvent(
                sec=0,
                usec=0,
                type=ecodes.EV_KEY,
                code=key_code,
                value=1 if press else 0
            )
            
            # Note: This approach may not work due to Linux security restrictions
            # We need to use uinput or alternative methods
            self.logger.warning(f"Direct key event injection not implemented for {device_path}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending key event: {e}")
            return False
    
    def send_caps_lock_hold(self, device_path: str, duration: float = 1.0):
        """Send Caps Lock hold command to toggle sensor ON/OFF"""
        try:
            self.logger.info(f"Sending Caps Lock hold ({duration}s) to {device_path}")
            
            # Press Caps Lock
            if not self.send_key_event(device_path, ecodes.KEY_CAPSLOCK, True):
                return False
            
            # Hold for specified duration
            time.sleep(duration)
            
            # Release Caps Lock
            if not self.send_key_event(device_path, ecodes.KEY_CAPSLOCK, False):
                return False
            
            self.logger.info(f"Caps Lock hold command sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending Caps Lock hold: {e}")
            return False
    
    def send_double_press(self, device_path: str, key_code: int):
        """Send double-press command to adjust intervals"""
        try:
            self.logger.info(f"Sending double-press to {device_path}")
            
            # First press
            if not self.send_key_event(device_path, key_code, True):
                return False
            time.sleep(0.05)
            if not self.send_key_event(device_path, key_code, False):
                return False
            
            # Brief pause
            time.sleep(0.1)
            
            # Second press
            if not self.send_key_event(device_path, key_code, True):
                return False
            time.sleep(0.05)
            if not self.send_key_event(device_path, key_code, False):
                return False
            
            self.logger.info(f"Double-press command sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending double-press: {e}")
            return False
    
    def increase_interval(self, device_path: str):
        """Increase sensor interval using double-press Caps Lock"""
        return self.send_double_press(device_path, ecodes.KEY_CAPSLOCK)
    
    def decrease_interval(self, device_path: str):
        """Decrease sensor interval using double-press Num Lock"""
        return self.send_double_press(device_path, ecodes.KEY_NUMLOCK)
    
    def toggle_sensor_on(self, device_path: str):
        """Toggle sensor ON using Caps Lock hold"""
        return self.send_caps_lock_hold(device_path, 1.0)
    
    def toggle_sensor_off(self, device_path: str):
        """Toggle sensor OFF using Caps Lock hold"""
        return self.send_caps_lock_hold(device_path, 1.0)
    
    def setup_udev_rules(self):
        """Setup udev rules for HID device access"""
        try:
            udev_rule = """# TemperhUM Sensor udev rules
# Allow access to HID devices for sensor control

# Generic HID keyboard devices
KERNEL=="hidraw*", SUBSYSTEM=="hidraw", MODE="0666"

# USB HID devices
SUBSYSTEM=="usb", ATTRS{idVendor}=="*", ATTRS{idProduct}=="*", MODE="0666"

# Input devices
KERNEL=="input*", SUBSYSTEM=="input", MODE="0666"
"""
            
            rule_path = "/etc/udev/rules.d/99-temperhum-sensors.rules"
            
            # Write rule file
            with open(rule_path, 'w') as f:
                f.write(udev_rule)
            
            # Reload udev rules
            subprocess.run(['udevadm', 'control', '--reload-rules'])
            subprocess.run(['udevadm', 'trigger'])
            
            self.logger.info(f"Udev rules installed: {rule_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up udev rules: {e}")
            return False
    
    def check_permissions(self):
        """Check if we have proper permissions for HID access"""
        try:
            # Check if user is in input group
            groups = subprocess.run(['groups'], capture_output=True, text=True)
            if 'input' in groups.stdout:
                self.logger.info("User is in input group")
                return True
            
            # Check if we can access /dev/input devices
            input_devices = os.listdir('/dev/input')
            if input_devices:
                self.logger.info("Can access /dev/input devices")
                return True
            
            self.logger.warning("May need elevated permissions for HID access")
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking permissions: {e}")
            return False
    
    def alternative_control_method(self, device_path: str, command: str):
        """Alternative method using external tools for HID control"""
        try:
            # Try using xdotool if available
            if command == "caps_lock_hold":
                subprocess.run(['xdotool', 'keydown', 'Caps_Lock'])
                time.sleep(1.0)
                subprocess.run(['xdotool', 'keyup', 'Caps_Lock'])
                self.logger.info("Used xdotool for Caps Lock hold")
                return True
            
            elif command == "double_caps":
                subprocess.run(['xdotool', 'key', 'Caps_Lock'])
                time.sleep(0.1)
                subprocess.run(['xdotool', 'key', 'Caps_Lock'])
                self.logger.info("Used xdotool for double Caps Lock")
                return True
            
            elif command == "double_num":
                subprocess.run(['xdotool', 'key', 'Num_Lock'])
                time.sleep(0.1)
                subprocess.run(['xdotool', 'key', 'Num_Lock'])
                self.logger.info("Used xdotool for double Num Lock")
                return True
            
            return False
            
        except FileNotFoundError:
            self.logger.warning("xdotool not available")
            return False
        except Exception as e:
            self.logger.error(f"Error with alternative control method: {e}")
            return False

def main():
    """Test the HID controller"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    controller = HIDController(logger)
    
    # Find devices
    devices = controller.find_temperhum_devices()
    
    if not devices:
        logger.error("No HID devices found")
        return
    
    # Check permissions
    if not controller.check_permissions():
        logger.warning("Permission issues detected")
    
    # Setup udev rules
    controller.setup_udev_rules()
    
    # Test with first device
    device = devices[0]
    logger.info(f"Testing with device: {device['name']}")
    
    # Try alternative control method
    if controller.alternative_control_method(device['path'], "caps_lock_hold"):
        logger.info("Alternative control method successful")
    else:
        logger.warning("Alternative control method failed")

if __name__ == '__main__':
    main() 