#!/usr/bin/env python3
"""
TemperhUM Sensor Integration - Phase 1 v2
Improved implementation that provides proper input targets for sensors.

This version:
1. Creates a focused text input area for sensors to type into
2. Uses xterm or similar to provide a proper keyboard input target
3. Captures sensor output in real-time
4. Provides live debugging output
"""

import os
import sys
import time
import logging
import subprocess
import threading
import select
import tempfile
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
        logging.FileHandler('/tmp/temperhum_phase1_v2.log')
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

class TemperhUMPhase1v2:
    """
    Phase 1 v2: Improved sensor control with proper input targets
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.sensors: Dict[str, SensorInfo] = {}
        self.data_file = "/tmp/temperhum_data.txt"
        self.terminal_process = None
        self.running = False
        self.data_thread = None
        
        # Clear previous data
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
    
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
    
    def create_input_target(self):
        """
        Create a focused input target for sensors to type into.
        Uses a terminal with a text editor or simple input area.
        """
        logger.info("📝 Creating input target for sensors...")
        
        try:
            # Method 1: Try using xterm with nano
            try:
                # Create a simple script that opens nano in a file
                script_content = f"""#!/bin/bash
echo "TemperhUM Sensor Data Capture"
echo "=============================="
echo "Sensors will type data here..."
echo ""
nano {self.data_file}
"""
                
                script_path = "/tmp/temperhum_capture.sh"
                with open(script_path, 'w') as f:
                    f.write(script_content)
                os.chmod(script_path, 0o755)
                
                # Start xterm with the script
                self.terminal_process = subprocess.Popen([
                    'xterm', '-title', 'TemperhUM Data Capture',
                    '-geometry', '80x24+100+100',
                    '-e', script_path
                ])
                
                logger.info("✅ Started xterm with nano editor")
                return True
                
            except Exception as e:
                logger.warning(f"xterm method failed: {e}")
                
                # Method 2: Try using gnome-terminal
                try:
                    self.terminal_process = subprocess.Popen([
                        'gnome-terminal', '--title=TemperhUM Data Capture',
                        '--', 'bash', '-c', f'nano {self.data_file}'
                    ])
                    
                    logger.info("✅ Started gnome-terminal with nano editor")
                    return True
                    
                except Exception as e2:
                    logger.warning(f"gnome-terminal method failed: {e2}")
                    
                    # Method 3: Try using konsole
                    try:
                        self.terminal_process = subprocess.Popen([
                            'konsole', '--title', 'TemperhUM Data Capture',
                            '-e', f'nano {self.data_file}'
                        ])
                        
                        logger.info("✅ Started konsole with nano editor")
                        return True
                        
                    except Exception as e3:
                        logger.warning(f"konsole method failed: {e3}")
                        
                        # Method 4: Fallback to simple file monitoring
                        logger.info("⚠️ No terminal available, using file monitoring only")
                        return False
        
        except Exception as e:
            logger.error(f"Failed to create input target: {e}")
            return False
    
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
        """
        logger.info("📝 Starting data capture...")
        
        # Create input target
        target_created = self.create_input_target()
        
        if target_created:
            # Wait for terminal to open
            time.sleep(3)
            
            # Give focus to the terminal window
            try:
                if self.terminal_process:
                    # Try to bring window to front
                    subprocess.run(['wmctrl', '-a', 'TemperhUM Data Capture'], 
                                 capture_output=True, timeout=5)
            except Exception as e:
                logger.debug(f"Could not focus window: {e}")
        
        # Start monitoring thread
        self.running = True
        self.data_thread = threading.Thread(target=self._monitor_data_file)
        self.data_thread.daemon = True
        self.data_thread.start()
        
        logger.info(f"✅ Data capture started - monitoring {self.data_file}")
    
    def _monitor_data_file(self):
        """
        Monitor the data file for new sensor readings.
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
        
        if self.terminal_process:
            try:
                self.terminal_process.terminate()
                self.terminal_process.wait(timeout=5)
            except Exception as e:
                logger.warning(f"Could not terminate terminal: {e}")
        
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
        print("🧪 Phase 1 v2 Test: Improved Sensor Control with Input Targets")
        print("=" * 70)
        
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
            
            # Step 4: Monitor for data (45 seconds)
            print("\n4️⃣ Monitoring sensor data (45 seconds)...")
            print("   A terminal window should open with nano editor")
            print("   Sensors should start typing data into the editor")
            print("   Look for temperature/humidity readings below:")
            print("-" * 40)
            
            start_time = time.time()
            while time.time() - start_time < 45:
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
                    if len(content) > 200:  # More than just header
                        print(f"\n✅ Data capture successful - {len(content)} characters captured")
                        print("\n📄 Captured data:")
                        print("-" * 40)
                        print(content)
                        return True
                    else:
                        print(f"\n⚠️ Limited data captured - {len(content)} characters")
                        if content:
                            print("\n📄 Captured data:")
                            print("-" * 40)
                            print(content)
                        return False
            
            return False
            
        except Exception as e:
            print(f"\n💥 Phase 1 test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function for Phase 1 v2 testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TemperhUM Phase 1 v2: Improved Sensor Control')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--test', action='store_true', help='Run complete Phase 1 test')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    controller = TemperhUMPhase1v2(debug=args.debug)
    
    if args.test:
        success = controller.run_phase1_test()
        
        if success:
            print("\n✅ Phase 1 v2 Test PASSED!")
            print("Sensors are active and ready for Phase 2 (interval adjustment)")
        else:
            print("\n❌ Phase 1 v2 Test FAILED!")
            print("Please check sensor connections and try again")
            sys.exit(1)
    else:
        # Interactive mode
        print("🐢 TemperhUM Phase 1 v2: Improved Sensor Control")
        print("=" * 55)
        
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