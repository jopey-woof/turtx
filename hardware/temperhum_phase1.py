#!/usr/bin/env python3
"""
TemperhUM Sensor Integration - Phase 1
Simplified implementation focused on core sensor control and data capture.

This phase focuses on:
1. Detecting TemperhUM sensors
2. Sending Caps Lock commands to activate them
3. Capturing data output to a unified stream
4. Live display of sensor readings for debugging
"""

import os
import sys
import time
import logging
import subprocess
import threading
import select
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import evdev

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/temperhum_phase1.log')
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

class TemperhUMPhase1:
    """
    Phase 1: Core sensor control and data capture
    Focuses on getting sensors active and capturing their output
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.sensors: Dict[str, SensorInfo] = {}
        self.data_file = "/tmp/temperhum_data.txt"
        self.running = False
        self.data_thread = None
        
        # Clear previous data
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
    
    def detect_sensors(self) -> List[str]:
        """
        Detect TemperhUM sensors and return keyboard device paths.
        Each physical sensor has multiple interfaces - we want the keyboard ones.
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
                    elif event_path:
                        logger.info(f"ℹ️ Found non-keyboard device: {event_path} ({device_name})")
        
        except Exception as e:
            logger.error(f"Error detecting sensors: {e}")
        
        logger.info(f"Detected {len(keyboard_devices)} TemperhUM keyboard devices")
        return keyboard_devices
    
    def send_caps_lock_hold(self, device_path: str, duration: float = 1.0) -> bool:
        """
        Send a Caps Lock hold command to a sensor device.
        Uses evdev to send the command directly to the device.
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
    
    def start_data_capture(self):
        """
        Start capturing data from all active sensors.
        Creates a unified data stream that both sensors type into.
        """
        logger.info("📝 Starting data capture...")
        
        # Create a simple text file for sensors to type into
        with open(self.data_file, 'w') as f:
            f.write("TemperhUM Data Capture Started\n")
            f.write("=" * 40 + "\n")
        
        # Start monitoring thread
        self.running = True
        self.data_thread = threading.Thread(target=self._monitor_data_file)
        self.data_thread.daemon = True
        self.data_thread.start()
        
        logger.info(f"✅ Data capture started - monitoring {self.data_file}")
    
    def _monitor_data_file(self):
        """
        Monitor the data file for new sensor readings.
        Displays live data for debugging.
        """
        logger.info("👀 Starting data file monitor...")
        
        last_size = 0
        
        while self.running:
            try:
                if os.path.exists(self.data_file):
                    current_size = os.path.getsize(self.data_file)
                    
                    if current_size > last_size:
                        # Read new content
                        with open(self.data_file, 'r') as f:
                            f.seek(last_size)
                            new_content = f.read()
                            
                            if new_content.strip():
                                # Display new data
                                lines = new_content.strip().split('\n')
                                for line in lines:
                                    if line.strip():
                                        print(f"📊 SENSOR DATA: {line.strip()}")
                                        logger.info(f"Sensor output: {line.strip()}")
                        
                        last_size = current_size
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Error monitoring data file: {e}")
                time.sleep(1)
    
    def stop_data_capture(self):
        """
        Stop data capture and cleanup.
        """
        logger.info("🛑 Stopping data capture...")
        self.running = False
        
        if self.data_thread and self.data_thread.is_alive():
            self.data_thread.join(timeout=5)
        
        logger.info("✅ Data capture stopped")
    
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
    
    def run_phase1_test(self) -> bool:
        """
        Run the complete Phase 1 test sequence.
        """
        print("🧪 Phase 1 Test: Core Sensor Control and Data Capture")
        print("=" * 60)
        
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
            
            # Step 3: Start data capture
            print("\n3️⃣ Starting data capture...")
            self.start_data_capture()
            
            # Step 4: Monitor for data (30 seconds)
            print("\n4️⃣ Monitoring sensor data (30 seconds)...")
            print("   Sensors should start typing data into the capture file")
            print("   Look for temperature/humidity readings below:")
            print("-" * 40)
            
            start_time = time.time()
            while time.time() - start_time < 30:
                time.sleep(1)
                # Data monitoring happens in background thread
            
            # Step 5: Stop and report
            print("\n5️⃣ Stopping data capture...")
            self.stop_data_capture()
            
            # Final status
            print("\n📊 Final Sensor Status:")
            status = self.get_sensor_status()
            for device_path, info in status.items():
                print(f"  {device_path}:")
                print(f"    Name: {info['name']}")
                print(f"    Active: {info['is_active']}")
                print(f"    Last Activity: {info['last_activity']}")
            
            # Check if we got any data
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    content = f.read()
                    if len(content) > 100:  # More than just header
                        print(f"\n✅ Data capture successful - {len(content)} characters captured")
                        return True
                    else:
                        print(f"\n⚠️ Limited data captured - {len(content)} characters")
                        return False
            
            return False
            
        except Exception as e:
            print(f"\n💥 Phase 1 test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function for Phase 1 testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TemperhUM Phase 1: Core Sensor Control')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--test', action='store_true', help='Run complete Phase 1 test')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    controller = TemperhUMPhase1(debug=args.debug)
    
    if args.test:
        success = controller.run_phase1_test()
        
        if success:
            print("\n✅ Phase 1 Test PASSED!")
            print("Sensors are active and ready for Phase 2 (interval adjustment)")
        else:
            print("\n❌ Phase 1 Test FAILED!")
            print("Please check sensor connections and try again")
            sys.exit(1)
    else:
        # Interactive mode
        print("🐢 TemperhUM Phase 1: Core Sensor Control")
        print("=" * 50)
        
        # Detect sensors
        devices = controller.detect_sensors()
        if devices:
            print(f"Detected {len(devices)} TemperhUM keyboard devices")
            
            # Activate sensors
            results = controller.activate_all_sensors()
            active_count = sum(1 for success in results.values() if success)
            print(f"Activated {active_count}/{len(devices)} sensors")
            
            # Start data capture
            controller.start_data_capture()
            print("Data capture started. Press Ctrl+C to stop...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                controller.stop_data_capture()
                print("\nStopped by user")

if __name__ == "__main__":
    main() 