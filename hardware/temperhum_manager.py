#!/usr/bin/env python3
"""
🐢 TEMPerHUM USB Sensor Manager - Fresh Implementation
=====================================================

This module manages TEMPerHUM USB temperature/humidity sensors that behave as HID keyboard devices.
The sensors "type" their data as keyboard input, which we capture and parse.

Key Features:
- Handles HID keyboard input from TEMPerHUM sensors
- Robust initialization and state management
- Comprehensive error handling and data validation
- MQTT integration for Home Assistant
- Multi-sensor support with device identification
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from pathlib import Path

# Third-party imports
try:
    import paho.mqtt.client as mqtt
    import evdev
    from evdev import categorize, ecodes
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("Install with: pip install paho-mqtt evdev")
    sys.exit(1)

# Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "turtle/sensors/temperhum"
LOG_FILE = "/var/log/temperhum-manager.log"
SENSOR_DATA_DIR = "/tmp/temperhum_data"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SensorReading:
    """Represents a single sensor reading"""
    temperature: float
    humidity: float
    timestamp: datetime
    interval: int
    sensor_id: str
    raw_data: str

class TemperhumSensor:
    """Individual TEMPerHUM sensor management"""
    
    def __init__(self, device_path: str, sensor_id: str):
        self.device_path = device_path
        self.sensor_id = sensor_id
        self.device = None
        self.is_active = False
        self.data_file = Path(SENSOR_DATA_DIR) / f"sensor_{sensor_id}.txt"
        self.last_reading = None
        self.banner_received = False
        self.activation_time = None
        
        # Ensure data directory exists
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized sensor {sensor_id} at {device_path}")
    
    def initialize_device(self) -> bool:
        """Initialize the HID device for reading"""
        try:
            self.device = evdev.InputDevice(self.device_path)
            logger.info(f"✅ Device {self.sensor_id} initialized: {self.device.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize device {self.sensor_id}: {e}")
            return False
    
    def send_caps_lock(self, duration: float = 1.0) -> bool:
        """Send Caps Lock key press to toggle sensor output"""
        try:
            # Create a virtual keyboard event
            uinput_device = evdev.UInput.from_device(self.device, name=f'temperhum-control-{self.sensor_id}')
            
            # Send Caps Lock press
            uinput_device.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_CAPSLOCK, 1)
            uinput_device.write(evdev.ecodes.EV_SYN, evdev.ecodes.SYN_REPORT, 0)
            
            time.sleep(duration)
            
            # Send Caps Lock release
            uinput_device.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_CAPSLOCK, 0)
            uinput_device.write(evdev.ecodes.EV_SYN, evdev.ecodes.SYN_REPORT, 0)
            
            uinput_device.close()
            logger.info(f"📡 Sent Caps Lock to sensor {self.sensor_id} for {duration}s")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send Caps Lock to sensor {self.sensor_id}: {e}")
            return False
    
    def activate_sensor(self) -> bool:
        """Activate the sensor by sending Caps Lock and waiting for banner"""
        logger.info(f"🚀 Activating sensor {self.sensor_id}...")
        
        # Send Caps Lock to toggle output
        if not self.send_caps_lock(1.0):
            return False
        
        # Wait for banner output (up to 10 seconds)
        start_time = time.time()
        banner_timeout = 10
        
        while time.time() - start_time < banner_timeout:
            if self.check_for_banner():
                self.is_active = True
                self.activation_time = datetime.now()
                logger.info(f"✅ Sensor {self.sensor_id} activated successfully")
                return True
            time.sleep(0.1)
        
        logger.warning(f"⚠️  Sensor {self.sensor_id} banner not received within {banner_timeout}s")
        return False
    
    def check_for_banner(self) -> bool:
        """Check if banner text has been received"""
        if self.banner_received:
            return True
            
        try:
            if self.data_file.exists():
                content = self.data_file.read_text()
                if any(banner in content.upper() for banner in [
                    'WWW.PCSENSOR.COM', 'TEMPERHUM', 'CAPS LOCK', 'NUM LOCK'
                ]):
                    self.banner_received = True
                    logger.info(f"📋 Banner received for sensor {self.sensor_id}")
                    return True
        except Exception as e:
            logger.debug(f"Error checking banner for sensor {self.sensor_id}: {e}")
        
        return False
    
    def read_data(self) -> Optional[SensorReading]:
        """Read and parse sensor data from the data file"""
        try:
            if not self.data_file.exists():
                return None
            
            # Read the last few lines to get recent data
            lines = self.data_file.read_text().splitlines()
            recent_lines = lines[-10:]  # Last 10 lines
            
            for line in reversed(recent_lines):
                reading = self.parse_data_line(line)
                if reading:
                    return reading
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error reading data from sensor {self.sensor_id}: {e}")
            return None
    
    def parse_data_line(self, line: str) -> Optional[SensorReading]:
        """Parse a single line of sensor data"""
        try:
            # Expected format: 29.54[C]39.58[%RH]1S
            # Handle variations in spacing and formatting
            line = line.strip()
            
            # Skip banner lines and empty lines
            if not line or any(banner in line.upper() for banner in [
                'WWW.PCSENSOR.COM', 'TEMPERHUM', 'CAPS LOCK', 'NUM LOCK', 'TYPE:'
            ]):
                return None
            
            # Extract temperature and humidity using regex-like parsing
            parts = line.split('[')
            if len(parts) < 3:
                return None
            
            # Parse temperature
            temp_part = parts[0].strip()
            if not temp_part.replace('.', '').replace('-', '').isdigit():
                return None
            temperature = float(temp_part)
            
            # Parse humidity
            hum_part = parts[1].split(']')[0].replace('%RH', '').strip()
            if not hum_part.replace('.', '').isdigit():
                return None
            humidity = float(hum_part)
            
            # Parse interval (last part)
            interval_part = parts[-1].split(']')[-1].replace('S', '').strip()
            interval = int(interval_part) if interval_part.isdigit() else 1
            
            # Validate reasonable ranges
            if not (-50 <= temperature <= 100):
                logger.warning(f"⚠️  Invalid temperature reading: {temperature}°C")
                return None
            
            if not (0 <= humidity <= 100):
                logger.warning(f"⚠️  Invalid humidity reading: {humidity}%")
                return None
            
            return SensorReading(
                temperature=temperature,
                humidity=humidity,
                timestamp=datetime.now(),
                interval=interval,
                sensor_id=self.sensor_id,
                raw_data=line
            )
            
        except Exception as e:
            logger.debug(f"Failed to parse line '{line}' for sensor {self.sensor_id}: {e}")
            return None
    
    def cleanup(self):
        """Clean up sensor resources"""
        try:
            if self.device:
                self.device.close()
            logger.info(f"🧹 Cleaned up sensor {self.sensor_id}")
        except Exception as e:
            logger.error(f"❌ Error cleaning up sensor {self.sensor_id}: {e}")

class TemperhumManager:
    """Main manager for multiple TEMPerHUM sensors"""
    
    def __init__(self):
        self.sensors: Dict[str, TemperhumSensor] = {}
        self.mqtt_client = None
        self.running = False
        self.data_thread = None
        
        # Initialize MQTT
        self.setup_mqtt()
        
        logger.info("🐢 TEMPerHUM Manager initialized")
    
    def setup_mqtt(self):
        """Setup MQTT client for publishing sensor data"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            
            # Connect to MQTT broker
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            
            logger.info(f"📡 MQTT connected to {MQTT_BROKER}:{MQTT_PORT}")
            
        except Exception as e:
            logger.error(f"❌ MQTT setup failed: {e}")
            self.mqtt_client = None
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("✅ MQTT connection established")
        else:
            logger.error(f"❌ MQTT connection failed with code {rc}")
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.warning(f"⚠️  MQTT disconnected with code {rc}")
    
    def discover_sensors(self) -> List[str]:
        """Discover TEMPerHUM sensors connected to the system"""
        sensor_paths = []
        
        try:
            # List all input devices
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            
            for device in devices:
                # Look for HID devices that might be TEMPerHUM sensors
                if device.info.bustype == evdev.ecodes.BUS_USB:
                    # Check if device has keyboard capabilities
                    if evdev.ecodes.EV_KEY in device.capabilities():
                        # Look for TEMPerHUM-specific identifiers
                        device_name = device.name.lower()
                        if any(keyword in device_name for keyword in [
                            'temperhum', 'pcsensor', 'hid', 'keyboard'
                        ]):
                            logger.info(f"🔍 Found potential TEMPerHUM sensor: {device.name} at {device.path}")
                            sensor_paths.append(device.path)
            
            logger.info(f"📊 Found {len(sensor_paths)} potential TEMPerHUM sensor(s)")
            return sensor_paths
            
        except Exception as e:
            logger.error(f"❌ Error discovering sensors: {e}")
            return []
    
    def initialize_sensors(self) -> bool:
        """Initialize all discovered sensors"""
        sensor_paths = self.discover_sensors()
        
        if not sensor_paths:
            logger.error("❌ No TEMPerHUM sensors found!")
            return False
        
        # Initialize each sensor
        for i, device_path in enumerate(sensor_paths):
            sensor_id = f"sensor_{i+1}"
            sensor = TemperhumSensor(device_path, sensor_id)
            
            if sensor.initialize_device():
                self.sensors[sensor_id] = sensor
                logger.info(f"✅ Initialized sensor {sensor_id}")
            else:
                logger.error(f"❌ Failed to initialize sensor {sensor_id}")
        
        if not self.sensors:
            logger.error("❌ No sensors could be initialized!")
            return False
        
        logger.info(f"✅ Successfully initialized {len(self.sensors)} sensor(s)")
        return True
    
    def activate_all_sensors(self) -> bool:
        """Activate all sensors"""
        success_count = 0
        
        for sensor_id, sensor in self.sensors.items():
            if sensor.activate_sensor():
                success_count += 1
            else:
                logger.error(f"❌ Failed to activate sensor {sensor_id}")
        
        logger.info(f"📡 Activated {success_count}/{len(self.sensors)} sensors")
        return success_count > 0
    
    def publish_sensor_data(self, sensor_id: str, reading: SensorReading):
        """Publish sensor data to MQTT"""
        if not self.mqtt_client:
            return
        
        try:
            topic = f"{MQTT_TOPIC_PREFIX}/{sensor_id}"
            
            data = {
                "temperature": reading.temperature,
                "humidity": reading.humidity,
                "timestamp": reading.timestamp.isoformat(),
                "interval": reading.interval,
                "sensor_id": sensor_id,
                "raw_data": reading.raw_data
            }
            
            payload = json.dumps(data)
            self.mqtt_client.publish(topic, payload, qos=1, retain=True)
            
            logger.debug(f"📤 Published data for {sensor_id}: {reading.temperature}°C, {reading.humidity}%")
            
        except Exception as e:
            logger.error(f"❌ Error publishing data for {sensor_id}: {e}")
    
    def publish_status(self, status: str):
        """Publish manager status to MQTT"""
        if not self.mqtt_client:
            return
        
        try:
            topic = f"{MQTT_TOPIC_PREFIX}/status"
            data = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "sensor_count": len(self.sensors),
                "active_sensors": [s_id for s_id, sensor in self.sensors.items() if sensor.is_active]
            }
            
            payload = json.dumps(data)
            self.mqtt_client.publish(topic, payload, qos=1, retain=True)
            
        except Exception as e:
            logger.error(f"❌ Error publishing status: {e}")
    
    def data_collection_loop(self):
        """Main data collection loop"""
        logger.info("🔄 Starting data collection loop...")
        
        while self.running:
            try:
                # Collect data from all sensors
                for sensor_id, sensor in self.sensors.items():
                    if sensor.is_active:
                        reading = sensor.read_data()
                        if reading:
                            self.publish_sensor_data(sensor_id, reading)
                
                # Publish status every 30 seconds
                if int(time.time()) % 30 == 0:
                    self.publish_status("running")
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"❌ Error in data collection loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def start(self):
        """Start the TEMPerHUM manager"""
        logger.info("🚀 Starting TEMPerHUM manager...")
        
        try:
            # Initialize sensors
            if not self.initialize_sensors():
                logger.error("❌ Failed to initialize sensors!")
                return False
            
            # Activate sensors
            if not self.activate_all_sensors():
                logger.warning("⚠️  Some sensors failed to activate")
            
            # Start data collection
            self.running = True
            self.data_thread = threading.Thread(target=self.data_collection_loop, daemon=True)
            self.data_thread.start()
            
            self.publish_status("started")
            logger.info("✅ TEMPerHUM manager started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start TEMPerHUM manager: {e}")
            return False
    
    def stop(self):
        """Stop the TEMPerHUM manager"""
        logger.info("🛑 Stopping TEMPerHUM manager...")
        
        self.running = False
        
        # Wait for data thread to finish
        if self.data_thread and self.data_thread.is_alive():
            self.data_thread.join(timeout=5)
        
        # Cleanup sensors
        for sensor in self.sensors.values():
            sensor.cleanup()
        
        # Disconnect MQTT
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        self.publish_status("stopped")
        logger.info("✅ TEMPerHUM manager stopped")

def main():
    """Main entry point"""
    logger.info("🐢 TEMPerHUM Manager - Fresh Implementation")
    logger.info("=" * 50)
    
    manager = TemperhumManager()
    
    try:
        if manager.start():
            # Keep running until interrupted
            while True:
                time.sleep(1)
        else:
            logger.error("❌ Failed to start manager")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Fatal error in TEMPerHUM manager: {e}")
    finally:
        manager.stop()
        logger.info("🧹 TEMPerHUM manager cleanup completed")

if __name__ == "__main__":
    main() 