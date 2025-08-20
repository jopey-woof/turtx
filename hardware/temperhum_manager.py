#!/usr/bin/env python3
"""
TEMPerHUM USB Sensor Manager
Comprehensive sensor management for TEMPerHUM USB temperature/humidity sensors

Features:
- Multi-sensor support (up to 2 sensors)
- Robust initialization and activation
- Error-resistant data parsing
- MQTT integration for Home Assistant
- Systemd service compatibility
- Comprehensive logging and error handling
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import paho.mqtt.client as mqtt
import hid
import re

# Configuration
TEMPERHUM_VENDOR_ID = 0x3553
TEMPERHUM_PRODUCT_ID = 0xa001
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = "turtle/sensors/temperhum"
LOG_LEVEL = logging.INFO

# Data validation ranges
MIN_TEMPERATURE = -40.0
MAX_TEMPERATURE = 80.0
MIN_HUMIDITY = 0.0
MAX_HUMIDITY = 100.0

class TEMPerHUMSensor:
    """Individual TEMPerHUM sensor management"""
    
    def __init__(self, device_path: str, sensor_id: int):
        self.device_path = device_path
        self.sensor_id = sensor_id
        self.device = None
        self.is_active = False
        self.last_data = None
        self.last_update = None
        self.error_count = 0
        self.max_errors = 5
        self.logger = logging.getLogger(f"TEMPerHUM-{sensor_id}")
        
    def __str__(self):
        return f"TEMPerHUM-{self.sensor_id} ({self.device_path})"
    
    def initialize(self) -> bool:
        """Initialize and activate the sensor"""
        try:
            self.logger.info(f"Initializing {self}")
            
            # Open HID device
            self.device = hid.Device(TEMPERHUM_VENDOR_ID, TEMPERHUM_PRODUCT_ID)
            self.logger.info(f"Device opened successfully: {self.device_path}")
            
            # Activate sensor (send Caps Lock to toggle ON)
            self._activate_sensor()
            
            # Wait for banner and validate
            if self._wait_for_banner():
                self.is_active = True
                self.logger.info(f"✅ {self} activated successfully")
                return True
            else:
                self.logger.error(f"❌ {self} failed to activate")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize {self}: {e}")
            return False
    
    def _activate_sensor(self):
        """Activate sensor by sending Caps Lock key"""
        try:
            # Send Caps Lock key to toggle sensor ON
            # This simulates pressing the physical button
            caps_lock_code = 0x39  # Caps Lock key code
            
            # Create HID report for Caps Lock
            report = [0x00, caps_lock_code, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            self.device.write(bytes(report))
            
            # Wait a moment for the key to be processed
            time.sleep(0.1)
            
            # Send key release
            release_report = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            self.device.write(bytes(release_report))
            
            self.logger.info(f"Sent activation command to {self}")
            
        except Exception as e:
            self.logger.error(f"Failed to activate {self}: {e}")
            raise
    
    def _wait_for_banner(self, timeout: int = 10) -> bool:
        """Wait for and validate banner output"""
        start_time = time.time()
        banner_detected = False
        
        self.logger.info(f"Waiting for banner from {self}...")
        
        while time.time() - start_time < timeout:
            try:
                # Read data from device
                data = self.device.read(64, timeout_ms=1000)
                if data:
                    data_str = data.decode('utf-8', errors='ignore')
                    self.logger.debug(f"Raw data from {self}: {data_str}")
                    
                    # Check for banner content
                    if "WWW.PCSENSOR.COM" in data_str or "TEMPERHUM" in data_str:
                        banner_detected = True
                        self.logger.info(f"✅ Banner detected from {self}")
                        break
                        
            except Exception as e:
                self.logger.debug(f"Read timeout/error from {self}: {e}")
                continue
        
        return banner_detected
    
    def read_data(self) -> Optional[Dict]:
        """Read and parse sensor data"""
        if not self.is_active or not self.device:
            return None
            
        try:
            # Read data from device
            data = self.device.read(64, timeout_ms=1000)
            if not data:
                return None
                
            data_str = data.decode('utf-8', errors='ignore')
            
            # Parse the data
            parsed = self._parse_data(data_str)
            if parsed:
                self.last_data = parsed
                self.last_update = datetime.now(timezone.utc)
                self.error_count = 0  # Reset error count on successful read
                return parsed
                
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error reading from {self}: {e}")
            
            if self.error_count >= self.max_errors:
                self.logger.error(f"Too many errors from {self}, deactivating")
                self.is_active = False
                
        return None
    
    def _parse_data(self, data_str: str) -> Optional[Dict]:
        """Parse sensor data with robust error handling"""
        try:
            # Remove any banner text that might appear
            data_str = self._clean_data(data_str)
            
            # Look for temperature and humidity pattern
            # Format: XX.XX[C]XX.XX[%RH]XS
            pattern = r'(\d+\.\d+)\[C\](\d+\.\d+)\[%RH\](\d+)S'
            match = re.search(pattern, data_str)
            
            if match:
                temp_c = float(match.group(1))
                humidity = float(match.group(2))
                interval = int(match.group(3))
                
                # Validate data ranges
                if (MIN_TEMPERATURE <= temp_c <= MAX_TEMPERATURE and 
                    MIN_HUMIDITY <= humidity <= MAX_HUMIDITY):
                    
                    # Convert to Fahrenheit
                    temp_f = (temp_c * 9/5) + 32
                    
                    return {
                        "temperature_c": round(temp_c, 2),
                        "temperature_f": round(temp_f, 2),
                        "humidity": round(humidity, 2),
                        "interval": interval,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "sensor_id": self.sensor_id
                    }
                else:
                    self.logger.warning(f"Data out of range from {self}: temp={temp_c}°C, humidity={humidity}%")
                    
            else:
                self.logger.debug(f"No valid data pattern found in: {data_str}")
                
        except Exception as e:
            self.logger.error(f"Error parsing data from {self}: {e}")
            
        return None
    
    def _clean_data(self, data_str: str) -> str:
        """Clean data string by removing banner text and other artifacts"""
        # Remove common banner text
        banner_patterns = [
            r'WWW\.PCSENSOR\.COM.*?INTERVAL',
            r'TEMPERHUM.*?INTERVAL',
            r'CAPS LOCK.*?INTERVAL',
            r'TYPE:.*?INTERVAL'
        ]
        
        for pattern in banner_patterns:
            data_str = re.sub(pattern, '', data_str, flags=re.DOTALL)
        
        # Remove extra whitespace and newlines
        data_str = re.sub(r'\s+', '', data_str)
        
        return data_str
    
    def close(self):
        """Close the sensor device"""
        if self.device:
            try:
                self.device.close()
                self.logger.info(f"Closed {self}")
            except Exception as e:
                self.logger.error(f"Error closing {self}: {e}")
            finally:
                self.device = None
                self.is_active = False


class TEMPerHUMManager:
    """Main manager for multiple TEMPerHUM sensors"""
    
    def __init__(self):
        self.sensors: List[TEMPerHUMSensor] = []
        self.mqtt_client = None
        self.running = False
        self.logger = logging.getLogger("TEMPerHUMManager")
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=LOG_LEVEL,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/temperhum-manager.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def discover_sensors(self) -> int:
        """Discover and initialize TEMPerHUM sensors"""
        try:
            self.logger.info("🔍 Discovering TEMPerHUM sensors...")
            
            # Find all TEMPerHUM devices
            devices = list(hid.enumerate(TEMPERHUM_VENDOR_ID, TEMPERHUM_PRODUCT_ID))
            
            if not devices:
                self.logger.warning("No TEMPerHUM devices found")
                return 0
            
            self.logger.info(f"Found {len(devices)} TEMPerHUM device(s)")
            
            # Initialize each sensor
            for i, device_info in enumerate(devices):
                sensor = TEMPerHUMSensor(device_info['path'], i + 1)
                
                if sensor.initialize():
                    self.sensors.append(sensor)
                    self.logger.info(f"✅ Sensor {i+1} initialized successfully")
                else:
                    self.logger.error(f"❌ Failed to initialize sensor {i+1}")
            
            self.logger.info(f"Successfully initialized {len(self.sensors)} sensor(s)")
            return len(self.sensors)
            
        except Exception as e:
            self.logger.error(f"Error discovering sensors: {e}")
            return 0
    
    def setup_mqtt(self) -> bool:
        """Setup MQTT client for Home Assistant integration"""
        try:
            self.logger.info("🔌 Setting up MQTT connection...")
            
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            # Connect to MQTT broker
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            
            self.logger.info("✅ MQTT connection established")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup MQTT: {e}")
            return False
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.logger.info("✅ Connected to MQTT broker")
        else:
            self.logger.error(f"❌ Failed to connect to MQTT broker, code: {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.logger.warning(f"Disconnected from MQTT broker, code: {rc}")
    
    def publish_data(self, sensor_data: Dict):
        """Publish sensor data to MQTT"""
        if not self.mqtt_client:
            return
            
        try:
            sensor_id = sensor_data['sensor_id']
            topic = f"{MQTT_TOPIC_PREFIX}/sensor_{sensor_id}"
            
            # Create Home Assistant compatible payload
            payload = {
                "temperature_c": sensor_data['temperature_c'],
                "temperature_f": sensor_data['temperature_f'],
                "humidity": sensor_data['humidity'],
                "interval": sensor_data['interval'],
                "timestamp": sensor_data['timestamp'],
                "unit_of_measurement": {
                    "temperature_c": "°C",
                    "temperature_f": "°F",
                    "humidity": "%"
                }
            }
            
            # Publish to MQTT
            result = self.mqtt_client.publish(
                topic, 
                json.dumps(payload), 
                qos=1, 
                retain=True
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published data for sensor {sensor_id}")
            else:
                self.logger.error(f"Failed to publish data for sensor {sensor_id}")
                
        except Exception as e:
            self.logger.error(f"Error publishing data: {e}")
    
    def run(self):
        """Main run loop"""
        self.running = True
        self.logger.info("🚀 Starting TEMPerHUM manager...")
        
        # Discover sensors
        sensor_count = self.discover_sensors()
        if sensor_count == 0:
            self.logger.error("No sensors available, exiting")
            return
        
        # Setup MQTT
        if not self.setup_mqtt():
            self.logger.error("Failed to setup MQTT, exiting")
            return
        
        self.logger.info(f"✅ TEMPerHUM manager running with {sensor_count} sensor(s)")
        
        try:
            while self.running:
                # Read data from all sensors
                for sensor in self.sensors:
                    if sensor.is_active:
                        data = sensor.read_data()
                        if data:
                            self.publish_data(data)
                            self.logger.info(f"Sensor {sensor.sensor_id}: {data['temperature_f']}°F, {data['humidity']}%")
                
                # Wait before next reading
                time.sleep(5)  # 5 second interval
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the manager"""
        self.logger.info("🛑 Shutting down TEMPerHUM manager...")
        self.running = False
        
        # Close all sensors
        for sensor in self.sensors:
            sensor.close()
        
        # Disconnect MQTT
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        self.logger.info("✅ TEMPerHUM manager shutdown complete")


def main():
    """Main entry point"""
    manager = TEMPerHUMManager()
    manager.run()


if __name__ == "__main__":
    main() 