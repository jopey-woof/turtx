#!/usr/bin/env python3
"""
TemperhUM MQTT Service - Production sensor service for turtle monitoring
Integrates TemperhUM sensors with Home Assistant via MQTT auto-discovery
"""
import os
import sys
import json
import time
import logging
import threading
import signal
import socket
from datetime import datetime
from typing import Dict, Optional, Any
import paho.mqtt.client as mqtt

# Import our working sensor controller
from temperhum_controller import TemperhUMController

class TemperhUMMQTTService:
    """Production MQTT service for TemperhUM sensors"""
    
    def __init__(self, config_file: str = None):
        # If no config file specified, look for it in the same directory as this script
        if config_file is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(script_dir, 'temperhum_config.json')
        
        self.config = self.load_config(config_file)
        temperature_unit = self.config.get('service', {}).get('temperature_unit', 'celsius')
        print(f"Loading config from: {config_file}")
        print(f"Temperature unit: {temperature_unit}")
        self.controller = TemperhUMController(
            verbose=self.config.get('debug', False),
            temperature_unit=temperature_unit
        )
        self.mqtt_client = None
        self.running = False
        self.sensor_data = {}
        
        # Setup logging
        self.setup_logging()
        
        # MQTT configuration
        self.mqtt_config = self.config.get('mqtt', {})
        self.ha_config = self.config.get('homeassistant', {})
        
        # Device info for Home Assistant
        self.device_info = {
            "identifiers": ["turtle_temperhum_sensors"],
            "name": "Turtle Enclosure Sensors",
            "manufacturer": "PCsensor",
            "model": "TEMPerHUM V4.1",
            "sw_version": "1.0.0"
        }
        
        self.logger.info("TemperhUM MQTT Service initialized")
    
    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "mqtt": {
                "host": "localhost",
                "port": 1883,
                "username": None,
                "password": None,
                "client_id": "temperhum_sensors",
                "keepalive": 60
            },
            "homeassistant": {
                "discovery_prefix": "homeassistant",
                "node_id": "turtle_sensors",
                "device_class_temperature": "temperature",
                "device_class_humidity": "humidity",
                "unit_temperature": "°C",
                "unit_humidity": "%"
            },
            "sensors": {
                "sensor1": {
                    "name": "Turtle Shell Temperature",
                    "location": "shell",
                    "update_interval": 30
                },
                "sensor2": {
                    "name": "Turtle Enclosure Temperature", 
                    "location": "enclosure",
                    "update_interval": 30
                }
            },
            "service": {
                "update_interval": 30,
                "retry_attempts": 3,
                "retry_delay": 5,
                "temperature_unit": "celsius"
            },
            "debug": False
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge user config with defaults
                self.deep_merge(default_config, user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        return default_config
    
    def deep_merge(self, base: Dict, update: Dict) -> None:
        """Deep merge update dict into base dict"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self.deep_merge(base[key], value)
            else:
                base[key] = value
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = logging.DEBUG if self.config.get('debug', False) else logging.INFO
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('/var/log/temperhum-mqtt.log', mode='a')
            ]
        )
        
        self.logger = logging.getLogger('TemperhUMMQTT')
    
    def setup_mqtt(self) -> bool:
        """Setup MQTT client connection"""
        try:
            self.mqtt_client = mqtt.Client(
                client_id=self.mqtt_config['client_id'],
                protocol=mqtt.MQTTv311
            )
            
            # Setup callbacks
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            self.mqtt_client.on_message = self.on_mqtt_message
            
            # Setup authentication if provided
            if self.mqtt_config.get('username'):
                self.mqtt_client.username_pw_set(
                    self.mqtt_config['username'],
                    self.mqtt_config.get('password')
                )
            
            # Connect to MQTT broker
            self.logger.info(f"Connecting to MQTT broker at {self.mqtt_config['host']}:{self.mqtt_config['port']}")
            self.mqtt_client.connect(
                self.mqtt_config['host'],
                self.mqtt_config['port'],
                self.mqtt_config['keepalive']
            )
            
            # Start MQTT loop in background
            self.mqtt_client.loop_start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup MQTT: {e}")
            return False
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.logger.info("Connected to MQTT broker")
            self.setup_ha_discovery()
        else:
            self.logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.logger.warning(f"Disconnected from MQTT broker: {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        self.logger.debug(f"Received MQTT message: {msg.topic} = {msg.payload.decode()}")
    
    def setup_ha_discovery(self):
        """Setup Home Assistant MQTT auto-discovery - BULLETPROOF DYNAMIC VERSION"""
        self.logger.info("Setting up Home Assistant auto-discovery")
        
        discovery_prefix = self.ha_config['discovery_prefix']
        node_id = self.ha_config['node_id']
        
        # Get all actually detected sensors from the controller
        detected_sensors = self.controller.get_available_sensors()
        self.logger.info(f"Setting up discovery for detected sensors: {detected_sensors}")
        
        # Setup discovery for each detected sensor
        sensor_counter = 1
        for sensor_id in detected_sensors:
            # Try to get config for this sensor, or create default
            sensor_config = self.config.get('sensors', {}).get(sensor_id, {})
            if not sensor_config:
                # Create default config for unrecognized sensors
                sensor_config = {
                    'name': f'Turtle Sensor {sensor_counter}',
                    'location': f'location_{sensor_counter}'
                }
                self.logger.info(f"Created default config for {sensor_id}: {sensor_config}")
            
            sensor_name = sensor_config.get('name', f'Sensor {sensor_id}')
            location = sensor_config.get('location', 'unknown')
            
            # Temperature sensor discovery
            temp_config = {
                "name": f"{sensor_name} Temperature",
                "unique_id": f"{node_id}_{sensor_id}_temperature",
                "state_topic": f"turtle/sensors/{sensor_id}/temperature",
                "unit_of_measurement": self.ha_config['unit_temperature'],
                "device_class": self.ha_config['device_class_temperature'],
                "value_template": "{{ value | round(1) }}",
                "device": {
                    **self.device_info,
                    "name": f"Turtle {location.title()} Sensor"
                },
                "availability": {
                    "topic": f"turtle/sensors/{sensor_id}/availability",
                    "payload_available": "online",
                    "payload_not_available": "offline"
                }
            }
            
            # Humidity sensor discovery
            hum_config = {
                "name": f"{sensor_name} Humidity",
                "unique_id": f"{node_id}_{sensor_id}_humidity",
                "state_topic": f"turtle/sensors/{sensor_id}/humidity",
                "unit_of_measurement": self.ha_config['unit_humidity'],
                "device_class": self.ha_config['device_class_humidity'],
                "value_template": "{{ value | round(1) }}",
                "device": {
                    **self.device_info,
                    "name": f"Turtle {location.title()} Sensor"
                },
                "availability": {
                    "topic": f"turtle/sensors/{sensor_id}/availability",
                    "payload_available": "online",
                    "payload_not_available": "offline"
                }
            }
            
            # Publish discovery configs
            temp_topic = f"{discovery_prefix}/sensor/{node_id}_{sensor_id}_temp/config"
            hum_topic = f"{discovery_prefix}/sensor/{node_id}_{sensor_id}_hum/config"
            
            self.mqtt_client.publish(temp_topic, json.dumps(temp_config), retain=True)
            self.mqtt_client.publish(hum_topic, json.dumps(hum_config), retain=True)
            
            # Set initial availability
            avail_topic = f"turtle/sensors/{sensor_id}/availability"
            self.mqtt_client.publish(avail_topic, "online", retain=True)
            
            self.logger.info(f"Published HA discovery for {sensor_id}: {sensor_name}")
            sensor_counter += 1
    
    def read_sensors(self) -> Dict[str, Dict]:
        """Read data from all sensors"""
        try:
            return self.controller.read_all_sensors()
        except Exception as e:
            self.logger.error(f"Failed to read sensors: {e}")
            return {}
    
    def publish_sensor_data(self, sensor_id: str, data: Dict):
        """Publish sensor data to MQTT"""
        try:
            if 'error' in data:
                self.logger.warning(f"Sensor {sensor_id} error: {data['error']}")
                # Publish offline status
                avail_topic = f"turtle/sensors/{sensor_id}/availability"
                self.mqtt_client.publish(avail_topic, "offline", retain=True)
                return
            
            # Publish temperature (use primary temperature based on config)
            temp_value = None
            if 'internal_temperature' in data:
                # Use the primary temperature (already converted to preferred unit)
                temp_value = data['internal_temperature']
            elif 'internal_temperature_f' in data:
                # Fallback to Fahrenheit
                temp_value = data['internal_temperature_f']
            elif 'internal_temperature_c' in data:
                # Fallback to Celsius
                temp_value = data['internal_temperature_c']
            
            if temp_value is not None:
                temp_topic = f"turtle/sensors/{sensor_id}/temperature"
                temperature = round(temp_value, 1)
                self.mqtt_client.publish(temp_topic, temperature, retain=True)
            
            # Publish humidity
            if 'internal_humidity' in data:
                hum_topic = f"turtle/sensors/{sensor_id}/humidity"
                humidity = round(data['internal_humidity'], 1)
                self.mqtt_client.publish(hum_topic, humidity, retain=True)
            
            # Publish availability
            avail_topic = f"turtle/sensors/{sensor_id}/availability"
            self.mqtt_client.publish(avail_topic, "online", retain=True)
            
            # Store last reading
            self.sensor_data[sensor_id] = {
                'temperature': temp_value,
                'humidity': data.get('internal_humidity'),
                'timestamp': time.time()
            }
            
            unit_symbol = "°F" if self.config.get('service', {}).get('temperature_unit', 'celsius').lower() in ['fahrenheit', 'f'] else "°C"
            self.logger.debug(f"Published data for {sensor_id}: {temperature}{unit_symbol}, {humidity}%")
            
        except Exception as e:
            self.logger.error(f"Failed to publish data for {sensor_id}: {e}")
    
    def sensor_loop(self):
        """Main sensor reading loop"""
        self.logger.info("Starting sensor reading loop")
        
        retry_count = 0
        max_retries = self.config['service']['retry_attempts']
        retry_delay = self.config['service']['retry_delay']
        update_interval = self.config['service']['update_interval']
        
        while self.running:
            try:
                # Read sensor data
                sensor_readings = self.read_sensors()
                
                if sensor_readings:
                    retry_count = 0  # Reset retry counter on success
                    
                    # Publish each sensor's data
                    for sensor_id, data in sensor_readings.items():
                        self.publish_sensor_data(sensor_id, data)
                    
                    self.logger.debug(f"Updated {len(sensor_readings)} sensors")
                else:
                    retry_count += 1
                    self.logger.warning(f"No sensor data received (retry {retry_count}/{max_retries})")
                    
                    if retry_count >= max_retries:
                        self.logger.error("Max retries exceeded, marking sensors offline")
                        for sensor_id in self.config['sensors'].keys():
                            avail_topic = f"turtle/sensors/{sensor_id}/availability"
                            self.mqtt_client.publish(avail_topic, "offline", retain=True)
                        retry_count = 0  # Reset for next cycle
                
                # Wait for next update
                time.sleep(update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in sensor loop: {e}")
                retry_count += 1
                
                if retry_count >= max_retries:
                    self.logger.critical("Sensor loop failed too many times, stopping")
                    self.stop()
                    break
                
                time.sleep(retry_delay)
    
    def start(self):
        """Start the MQTT service"""
        self.logger.info("Starting TemperhUM MQTT Service")
        
        # Check if sensors are available
        if not self.controller.sensors:
            self.logger.error("No TemperhUM sensors found!")
            return False
        
        self.logger.info(f"Found {len(self.controller.sensors)} sensors: {list(self.controller.sensors.keys())}")
        
        # Setup MQTT connection
        if not self.setup_mqtt():
            self.logger.error("Failed to setup MQTT connection")
            return False
        
        # Wait for MQTT connection
        connection_timeout = 10
        start_time = time.time()
        while not self.mqtt_client.is_connected() and (time.time() - start_time) < connection_timeout:
            time.sleep(0.1)
        
        if not self.mqtt_client.is_connected():
            self.logger.error("Failed to connect to MQTT broker within timeout")
            return False
        
        # Start sensor reading loop
        self.running = True
        self.sensor_thread = threading.Thread(target=self.sensor_loop, daemon=True)
        self.sensor_thread.start()
        
        self.logger.info("TemperhUM MQTT Service started successfully")
        return True
    
    def stop(self):
        """Stop the MQTT service"""
        self.logger.info("Stopping TemperhUM MQTT Service")
        
        self.running = False
        
        # Mark sensors as offline
        if self.mqtt_client and self.mqtt_client.is_connected():
            for sensor_id in self.config['sensors'].keys():
                avail_topic = f"turtle/sensors/{sensor_id}/availability"
                self.mqtt_client.publish(avail_topic, "offline", retain=True)
        
        # Stop MQTT client
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        self.logger.info("TemperhUM MQTT Service stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully")
        self.stop()
        sys.exit(0)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TemperhUM MQTT Service for Home Assistant')
    parser.add_argument('-c', '--config', help='Configuration file path')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--test', action='store_true', help='Run sensor test and exit')
    
    args = parser.parse_args()
    
    # Override debug setting from command line
    if args.debug:
        if args.config:
            # Load config and set debug
            pass
        else:
            config = {"debug": True}
    
    # Check for root privileges (needed for hidraw access)
    if os.geteuid() != 0:
        print("ERROR: This service requires root privileges for USB sensor access")
        print("Please run with: sudo python3 temperhum_mqtt_service.py")
        sys.exit(1)
    
    # Create service instance
    service = TemperhUMMQTTService(config_file=args.config)
    
    if args.test:
        # Test mode - just read sensors once and exit
        print("Testing sensor connectivity...")
        sensor_data = service.read_sensors()
        
        if sensor_data:
            print("✅ Sensor test successful!")
            for sensor_id, data in sensor_data.items():
                if 'error' in data:
                    print(f"❌ {sensor_id}: {data['error']}")
                else:
                    temp = data.get('internal_temperature_c', 'N/A')
                    hum = data.get('internal_humidity', 'N/A')
                    print(f"✅ {sensor_id}: {temp}°C, {hum}%RH")
        else:
            print("❌ No sensor data received")
            sys.exit(1)
        
        sys.exit(0)
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, service.signal_handler)
    signal.signal(signal.SIGTERM, service.signal_handler)
    
    # Start the service
    if service.start():
        print("TemperhUM MQTT Service started. Press Ctrl+C to stop.")
        try:
            # Keep main thread alive
            while service.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to start TemperhUM MQTT Service")
        sys.exit(1)

if __name__ == "__main__":
    main()