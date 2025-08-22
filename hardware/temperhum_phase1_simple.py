#!/usr/bin/env python3
"""
TemperhUM Sensor Integration - Phase 1 Simple
Basic implementation for testing sensor activation.

This version focuses on:
1. Detecting TemperhUM sensors
2. Sending Caps Lock commands to activate them
3. Providing manual testing instructions
4. Basic data capture verification
"""

import os
import sys
import time
import logging
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass
import evdev

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/temperhum_phase1_simple.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SensorInfo:
    """Information about a detected TemperhUM sensor"""
    device_path: str
    device_name: str
    is_keyboard: bool
    is_active: bool = False
    last_activity: Optional[float] = None

class TemperhUMPhase1Simple:
    """
    Phase 1 Simple: Basic sensor control and manual testing
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.sensors: Dict[str, SensorInfo] = {}
    
    def detect_sensors(self) -> List[str]:
        """
        Detect TemperhUM sensors and return keyboard device paths.
        """
        logger.info("🔍 Detecting TemperhUM sensors...")
        
        keyboard_devices = []
        
        try:
            # Read device information
            with open('/proc/bus/input/devices', 'r') as f:
                content = f.read()
            
            # Parse device blocks
            device_blocks = content.split('\n\n')
            for block in device_blocks:
                if 'TEMPerHUM' in block or 'pcsensor' in block.lower():
                    logger.info(f"Found TemperhUM device:\n{block}")
                    
                    # Check if this is a keyboard device
                    is_keyboard = 'kbd' in block and 'sysrq' in block
                    device_name = "Unknown"
                    event_path = None
                    
                    # Extract device name and event path
                    for line in block.split('\n'):
                        if line.startswith('N: Name='):
                            device_name = line.split('=')[1].strip('"')
                        elif line.startswith('H: Handlers='):
                            handlers = line.split('=')[1]
                            if 'event' in handlers:
                                import re
                                event_match = re.search(r'event(\d+)', handlers)
                                if event_match:
                                    event_num = event_match.group(1)
                                    event_path = f"/dev/input/event{event_num}"
                    
                    if event_path and is_keyboard:
                        keyboard_devices.append(event_path)
                        self.sensors[event_path] = SensorInfo(
                            device_path=event_path,
                            device_name=device_name,
                            is_keyboard=True
                        )
                        logger.info(f"✅ Added keyboard device: {event_path} ({device_name})")
        
        except Exception as e:
            logger.error(f"Error detecting sensors: {e}")
        
        logger.info(f"Detected {len(keyboard_devices)} TemperhUM keyboard devices")
        return keyboard_devices
    
    def send_caps_lock_hold(self, device_path: str, duration: float = 1.0) -> bool:
        """
        Send a Caps Lock hold command to a sensor device.
        """
        logger.info(f"🔘 Sending Caps Lock hold ({duration}s) to {device_path}")
        
        try:
            # Open the device
            device = evdev.InputDevice(device_path)
            
            # Caps Lock key code
            caps_lock_code = evdev.ecodes.KEY_CAPSLOCK
            
            # Send key down
            device.write(evdev.ecodes.EV_KEY, caps_lock_code, 1)
            device.write(evdev.ecodes.EV_SYN, 0, 0)
            
            # Hold for duration
            time.sleep(duration)
            
            # Send key up
            device.write(evdev.ecodes.EV_KEY, caps_lock_code, 0)
            device.write(evdev.ecodes.EV_SYN, 0, 0)
            
            logger.info(f"✅ Caps Lock command sent to {device_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send Caps Lock to {device_path}: {e}")
            return False
    
    def send_double_press(self, device_path: str, key: str) -> bool:
        """
        Send a double-press command to adjust sensor intervals.
        """
        logger.info(f"🔘 Sending double-press {key} to {device_path}")
        
        try:
            if key == 'caps_lock':
                # Double-press Caps Lock to increase interval
                self.send_caps_lock_hold(device_path, 0.1)
                time.sleep(0.1)
                self.send_caps_lock_hold(device_path, 0.1)
                return True
            elif key == 'num_lock':
                # For Num Lock, we'd need to implement it
                logger.warning("Num Lock double-press not implemented")
                return False
            else:
                logger.error(f"Unknown key: {key}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send double-press {key}: {e}")
            return False
    
    def activate_sensor(self, device_path: str) -> bool:
        """
        Activate a single sensor by sending Caps Lock hold.
        """
        logger.info(f"🚀 Activating sensor: {device_path}")
        
        # Send Caps Lock hold to toggle ON
        if self.send_caps_lock_hold(device_path):
            self.sensors[device_path].is_active = True
            self.sensors[device_path].last_activity = time.time()
            logger.info(f"✅ Sensor {device_path} activated")
            return True
        else:
            logger.error(f"❌ Failed to activate sensor {device_path}")
            return False
    
    def activate_all_sensors(self) -> Dict[str, bool]:
        """
        Activate all detected TemperhUM sensors.
        """
        logger.info("🚀 Activating all TemperhUM sensors...")
        
        results = {}
        keyboard_devices = self.detect_sensors()
        
        if not keyboard_devices:
            logger.warning("⚠️ No TemperhUM keyboard devices detected")
            return results
        
        for device_path in keyboard_devices:
            success = self.activate_sensor(device_path)
            results[device_path] = success
            
            # Wait between sensors to avoid conflicts
            time.sleep(2)
        
        active_count = sum(1 for success in results.values() if success)
        logger.info(f"✅ Activation complete: {active_count}/{len(keyboard_devices)} sensors active")
        
        return results
    
    def configure_sensor_intervals(self):
        """
        Configure sensor intervals using double-press commands.
        """
        logger.info("⚙️ Configuring sensor intervals...")
        
        keyboard_devices = list(self.sensors.keys())
        
        if len(keyboard_devices) >= 1:
            # Configure Sensor 1 to 1-second interval
            logger.info("Configuring Sensor 1 to 1-second interval...")
            # This would require Num Lock double-press to decrease interval
            # For now, we'll just note that this needs to be done manually
            logger.info("⚠️ Manual interval configuration required")
        
        if len(keyboard_devices) >= 2:
            # Configure Sensor 2 to 2-second interval
            logger.info("Configuring Sensor 2 to 2-second interval...")
            # This would require Caps Lock double-press to increase interval
            logger.info("⚠️ Manual interval configuration required")
    
    def get_sensor_status(self) -> Dict[str, Dict]:
        """
        Get current status of all sensors.
        """
        status = {}
        for device_path, sensor in self.sensors.items():
            status[device_path] = {
                'name': sensor.device_name,
                'is_keyboard': sensor.is_keyboard,
                'is_active': sensor.is_active,
                'last_activity': sensor.last_activity
            }
        return status
    
    def print_manual_test_instructions(self):
        """
        Print instructions for manual testing.
        """
        print("\n📋 Manual Testing Instructions:")
        print("=" * 50)
        print("1. Open a text editor (nano, vim, or any text field)")
        print("2. Make sure the text editor has focus")
        print("3. The sensors should start typing data automatically")
        print("4. Look for data in this format:")
        print("   WWW.PCSENSOR.COM")
        print("   TEMPERHUM V4.1")
        print("   CAPS LOCK:ON/OFF/++")
        print("   NUM LOCK:OFF/ON/--")
        print("   TYPE:INNER-H3")
        print("   INNER-TEMPINNER-HUMINTERVAL")
        print("   Followed by readings like:")
        print("   29.54[C]39.58[%RH]1S")
        print("   29.59[C]39.63[%RH]1S")
        print("")
        print("5. If no data appears, try:")
        print("   - Pressing Caps Lock manually on the sensor")
        print("   - Checking if the sensor LED is on")
        print("   - Ensuring the text editor has focus")
        print("")
        print("6. To test interval adjustment:")
        print("   - Double-press Caps Lock to increase interval")
        print("   - Double-press Num Lock to decrease interval")
        print("")
        print("7. To stop sensor output:")
        print("   - Hold Caps Lock for 1 second")
    
    def run_phase1_test(self) -> bool:
        """
        Run the complete Phase 1 test sequence.
        """
        print("🧪 Phase 1 Simple Test: Basic Sensor Control")
        print("=" * 50)
        
        try:
            # Step 1: Detect sensors
            print("\n1️⃣ Detecting TemperhUM sensors...")
            keyboard_devices = self.detect_sensors()
            
            if not keyboard_devices:
                print("❌ No TemperhUM keyboard devices detected")
                return False
            
            print(f"✅ Detected {len(keyboard_devices)} keyboard devices")
            
            # Step 2: Activate sensors
            print("\n2️⃣ Activating sensors...")
            results = self.activate_all_sensors()
            
            active_count = sum(1 for success in results.values() if success)
            if active_count == 0:
                print("❌ No sensors were activated")
                return False
            
            print(f"✅ {active_count}/{len(keyboard_devices)} sensors activated")
            
            # Step 3: Configure intervals
            print("\n3️⃣ Configuring sensor intervals...")
            self.configure_sensor_intervals()
            
            # Step 4: Manual testing instructions
            print("\n4️⃣ Manual testing phase...")
            self.print_manual_test_instructions()
            
            # Step 5: Wait for user input
            print("\n5️⃣ Waiting for manual verification...")
            print("Please follow the instructions above to test sensor output.")
            print("Press Enter when you've verified sensor data is working...")
            input()
            
            # Step 6: Final status
            print("\n📊 Final Sensor Status:")
            status = self.get_sensor_status()
            for device_path, info in status.items():
                print(f"  {device_path}:")
                print(f"    Name: {info['name']}")
                print(f"    Active: {info['is_active']}")
                print(f"    Last Activity: {info['last_activity']}")
            
            print("\n✅ Phase 1 Simple test completed!")
            print("If you saw sensor data, Phase 1 is successful.")
            return True
            
        except Exception as e:
            print(f"\n💥 Phase 1 test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function for Phase 1 Simple testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TemperhUM Phase 1 Simple: Basic Sensor Control')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--test', action='store_true', help='Run complete Phase 1 test')
    parser.add_argument('--activate', action='store_true', help='Just activate sensors')
    parser.add_argument('--status', action='store_true', help='Show sensor status')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    controller = TemperhUMPhase1Simple(debug=args.debug)
    
    if args.test:
        success = controller.run_phase1_test()
        
        if success:
            print("\n✅ Phase 1 Simple Test PASSED!")
            print("Sensors are active and ready for Phase 2 (interval adjustment)")
        else:
            print("\n❌ Phase 1 Simple Test FAILED!")
            print("Please check sensor connections and try again")
            sys.exit(1)
    elif args.activate:
        # Just activate sensors
        print("🐢 Activating TemperhUM sensors...")
        results = controller.activate_all_sensors()
        active_count = sum(1 for success in results.values() if success)
        print(f"✅ {active_count} sensors activated")
        
        if active_count > 0:
            controller.print_manual_test_instructions()
    elif args.status:
        # Show status
        controller.detect_sensors()
        status = controller.get_sensor_status()
        print("📊 Sensor Status:")
        for device_path, info in status.items():
            print(f"  {device_path}:")
            print(f"    Name: {info['name']}")
            print(f"    Active: {info['is_active']}")
            print(f"    Last Activity: {info['last_activity']}")
    else:
        # Interactive mode
        print("🐢 TemperhUM Phase 1 Simple: Basic Sensor Control")
        print("=" * 55)
        
        # Detect sensors
        devices = controller.detect_sensors()
        if devices:
            print(f"Detected {len(devices)} TemperhUM keyboard devices")
            
            # Activate sensors
            results = controller.activate_all_sensors()
            active_count = sum(1 for success in results.values() if success)
            print(f"Activated {active_count}/{len(devices)} sensors")
            
            if active_count > 0:
                controller.print_manual_test_instructions()

if __name__ == "__main__":
    main() 