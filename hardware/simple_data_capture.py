#!/usr/bin/env python3
"""
Simple TemperhUM Data Capture
Captures sensor data from file input without complex HID control
"""

import os
import sys
import time
import json
import logging
import argparse
import subprocess
import threading
from datetime import datetime
from typing import Dict, Optional
import paho.mqtt.client as mqtt

# Configuration
CONFIG = {
    'mqtt_broker': 'localhost',
    'mqtt_port': 1883,
    'mqtt_username': None,
    'mqtt_password': None,
    'mqtt_base_topic': 'turtle/sensors/temperhum',
    'data_file': '/tmp/temperhum_data.txt',
    'log_file': '/var/log/temperhum-capture.log',
    'debug': False,
    'sensor_intervals': {
        'sensor_1': 1,  # 1-second intervals
        'sensor_2': 2   # 2-second intervals
    }
}

class SimpleDataCapture:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.running = False
        self.sensors = {}
        self.mqtt_client = None
        self.data_file = None
        
        # Setup logging
        self.setup_logging()
        
        # Initialize sensor data structure
        for sensor_id in ['sensor_1', 'sensor_2']:
            self.sensors[sensor_id] = {
                'temperature': None,
                'humidity': None,
                'timestamp': None,
                'interval': CONFIG['sensor_intervals'][sensor_id],
                'last_seen': None,
                'status': 'unknown',
                'data_count': 0
            }
    
    def setup_logging(self):
        """Configure logging"""
        log_level = logging.DEBUG if self.debug else logging.INFO
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup logger
        self.logger = logging.getLogger('SimpleDataCapture')
        self.logger.setLevel(log_level)
        
        # Console handler (always available)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (try to create, fallback if permission denied)
        try:
            file_handler = logging.FileHandler(CONFIG['log_file'])
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except PermissionError:
            # Fallback to temp file
            try:
                temp_log_file = '/tmp/temperhum-capture.log'
                file_handler = logging.FileHandler(temp_log_file)
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                self.logger.warning(f"Using temporary log file: {temp_log_file}")
            except Exception as e:
                self.logger.warning(f"Could not create log file: {e}")
        except Exception as e:
            self.logger.warning(f"Could not create log file: {e}")
        
        self.logger.info("Simple Data Capture initialized")
    
    def setup_data_file(self):
        """Setup the data capture file"""
        try:
            # Create data file if it doesn't exist
            if not os.path.exists(CONFIG['data_file']):
                with open(CONFIG['data_file'], 'w') as f:
                    f.write("# TemperhUM Sensor Data Capture\n")
                    f.write(f"# Started: {datetime.now().isoformat()}\n")
                    f.write("# Format: temperature[°C] humidity[%RH] interval[S]\n\n")
                
                self.logger.info(f"Created data capture file: {CONFIG['data_file']}")
            else:
                self.logger.info(f"Using existing data file: {CONFIG['data_file']}")
            
            # Open file for appending
            self.data_file = open(CONFIG['data_file'], 'a')
            
        except Exception as e:
            self.logger.error(f"Error setting up data file: {e}")
            raise
    
    def parse_sensor_data(self, raw_line: str) -> Optional[Dict]:
        """Parse sensor data line and identify sensor by interval"""
        try:
            # Remove whitespace and newlines
            line = raw_line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                return None
            
            # Skip banner text
            if any(banner in line.lower() for banner in [
                'www.pcsensor.com', 'temperhum', 'caps lock', 'num lock', 
                'type:', 'inner-', 'interval'
            ]):
                if self.debug:
                    print(f"DEBUG: Skipping banner line: {line}")
                return None
            
            # Parse data format: XX.XX[C]XX.XX[%RH]XS
            # Example: 29.54[C]39.58[%RH]1S
            import re
            pattern = r'(\d+\.\d+)\[C\](\d+\.\d+)\[%RH\](\d+)S'
            match = re.match(pattern, line)
            
            if not match:
                if self.debug:
                    print(f"DEBUG: Failed to parse line: {line}")
                return None
            
            temperature = float(match.group(1))
            humidity = float(match.group(2))
            interval = int(match.group(3))
            
            # Validate data ranges
            if not (0 <= temperature <= 50):
                self.logger.warning(f"Temperature out of range: {temperature}°C")
                return None
            
            if not (0 <= humidity <= 100):
                self.logger.warning(f"Humidity out of range: {humidity}%")
                return None
            
            # Identify sensor by interval
            sensor_id = None
            for sid, config in self.sensors.items():
                if config['interval'] == interval:
                    sensor_id = sid
                    break
            
            if not sensor_id:
                self.logger.warning(f"Unknown sensor interval: {interval}S")
                return None
            
            # Create parsed data
            parsed_data = {
                'sensor_id': sensor_id,
                'temperature': temperature,
                'humidity': humidity,
                'interval': interval,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'raw_line': line
            }
            
            if self.debug:
                print(f"DEBUG: Parsed {sensor_id}: {temperature}°C, {humidity}%RH, {interval}S")
            
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"Error parsing sensor data: {e}")
            return None
    
    def update_sensor_data(self, parsed_data: Dict):
        """Update sensor data structure with new readings"""
        sensor_id = parsed_data['sensor_id']
        
        self.sensors[sensor_id].update({
            'temperature': parsed_data['temperature'],
            'humidity': parsed_data['humidity'],
            'timestamp': parsed_data['timestamp'],
            'last_seen': parsed_data['timestamp'],
            'status': 'active',
            'data_count': self.sensors[sensor_id]['data_count'] + 1
        })
        
        self.logger.debug(f"Updated {sensor_id}: {parsed_data['temperature']}°C, {parsed_data['humidity']}%RH")
    
    def setup_mqtt(self):
        """Setup MQTT client and auto-discovery"""
        try:
            self.mqtt_client = mqtt.Client()
            
            # Set credentials if provided
            if CONFIG['mqtt_username'] and CONFIG['mqtt_password']:
                self.mqtt_client.username_pw_set(CONFIG['mqtt_username'], CONFIG['mqtt_password'])
            
            # Connect to broker
            self.mqtt_client.connect(CONFIG['mqtt_broker'], CONFIG['mqtt_port'], 60)
            self.mqtt_client.loop_start()
            
            self.logger.info("MQTT client connected")
            
            # Setup auto-discovery
            self.setup_mqtt_discovery()
            
        except Exception as e:
            self.logger.error(f"Error setting up MQTT: {e}")
            raise
    
    def setup_mqtt_discovery(self):
        """Setup Home Assistant MQTT auto-discovery"""
        try:
            # Create device configuration
            device_config = {
                "identifiers": ["turtle_temperhum_system"],
                "name": "Turtle Enclosure TemperhUM Sensors",
                "model": "TemperhUM V4.1",
                "manufacturer": "PCSensor",
                "sw_version": "1.0.0"
            }
            
            # Setup discovery for each sensor
            for sensor_id in ['sensor_1', 'sensor_2']:
                # Temperature sensor
                temp_config = {
                    "device": device_config,
                    "name": f"Turtle {sensor_id.replace('_', ' ').title()} Temperature",
                    "unique_id": f"turtle_{sensor_id}_temperature",
                    "state_topic": f"{CONFIG['mqtt_base_topic']}/{sensor_id}/temperature",
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "value_template": "{{ value | float | round(2) }}"
                }
                
                # Humidity sensor
                hum_config = {
                    "device": device_config,
                    "name": f"Turtle {sensor_id.replace('_', ' ').title()} Humidity",
                    "unique_id": f"turtle_{sensor_id}_humidity",
                    "state_topic": f"{CONFIG['mqtt_base_topic']}/{sensor_id}/humidity",
                    "unit_of_measurement": "%",
                    "device_class": "humidity",
                    "value_template": "{{ value | float | round(2) }}"
                }
                
                # Publish discovery messages
                temp_topic = f"homeassistant/sensor/turtle_{sensor_id}_temperature/config"
                hum_topic = f"homeassistant/sensor/turtle_{sensor_id}_humidity/config"
                
                self.mqtt_client.publish(temp_topic, json.dumps(temp_config), retain=True)
                self.mqtt_client.publish(hum_topic, json.dumps(hum_config), retain=True)
                
                self.logger.info(f"Published discovery config for {sensor_id}")
            
        except Exception as e:
            self.logger.error(f"Error setting up MQTT discovery: {e}")
    
    def publish_sensor_data(self, parsed_data: Dict):
        """Publish sensor data to MQTT"""
        try:
            sensor_id = parsed_data['sensor_id']
            base_topic = CONFIG['mqtt_base_topic']
            
            # Publish temperature
            temp_topic = f"{base_topic}/{sensor_id}/temperature"
            self.mqtt_client.publish(temp_topic, str(parsed_data['temperature']))
            
            # Publish humidity
            hum_topic = f"{base_topic}/{sensor_id}/humidity"
            self.mqtt_client.publish(hum_topic, str(parsed_data['humidity']))
            
            # Publish status
            status_topic = f"{base_topic}/{sensor_id}/status"
            self.mqtt_client.publish(status_topic, "online")
            
            self.logger.debug(f"Published {sensor_id} data to MQTT")
            
        except Exception as e:
            self.logger.error(f"Error publishing sensor data: {e}")
    
    def monitor_data_file(self):
        """Monitor the data file for new sensor readings"""
        self.logger.info("Starting data file monitoring...")
        
        try:
            # Use tail -f to monitor file
            process = subprocess.Popen(
                ['tail', '-f', CONFIG['data_file']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            while self.running:
                line = process.stdout.readline()
                if line:
                    # Parse the line
                    parsed_data = self.parse_sensor_data(line)
                    if parsed_data:
                        # Update sensor data
                        self.update_sensor_data(parsed_data)
                        
                        # Publish to MQTT
                        self.publish_sensor_data(parsed_data)
                        
                        # Live debug output
                        if self.debug:
                            print(f"LIVE: {parsed_data['sensor_id']} - "
                                  f"{parsed_data['temperature']}°C, "
                                  f"{parsed_data['humidity']}%RH, "
                                  f"{parsed_data['interval']}S")
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
            
        except Exception as e:
            self.logger.error(f"Error monitoring data file: {e}")
        finally:
            if process:
                process.terminate()
    
    def print_status(self):
        """Print current sensor status"""
        print("\n=== TemperhUM Sensor Status ===")
        for sensor_id, data in self.sensors.items():
            status = data['status']
            temp = data['temperature']
            hum = data['humidity']
            count = data['data_count']
            last_seen = data['last_seen']
            
            print(f"{sensor_id}:")
            print(f"  Status: {status}")
            print(f"  Temperature: {temp}°C" if temp else "  Temperature: No data")
            print(f"  Humidity: {hum}%RH" if hum else "  Humidity: No data")
            print(f"  Data count: {count}")
            print(f"  Last seen: {last_seen}" if last_seen else "  Last seen: Never")
            print()
    
    def start(self):
        """Start the data capture"""
        self.logger.info("Starting Simple Data Capture...")
        self.running = True
        
        try:
            # Setup data file
            self.setup_data_file()
            
            # Setup MQTT
            self.setup_mqtt()
            
            # Start monitoring in background thread
            monitor_thread = threading.Thread(target=self.monitor_data_file)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            self.logger.info("Simple Data Capture started successfully")
            
            # Print initial status
            self.print_status()
            
            # Keep main thread alive
            try:
                while self.running:
                    time.sleep(5)  # Print status every 5 seconds
                    if self.debug:
                        self.print_status()
            except KeyboardInterrupt:
                self.logger.info("Received shutdown signal")
                
        except Exception as e:
            self.logger.error(f"Error starting capture: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop the data capture"""
        self.logger.info("Stopping Simple Data Capture...")
        self.running = False
        
        # Close data file
        if self.data_file:
            self.data_file.close()
        
        # Disconnect MQTT
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        # Print final status
        self.print_status()
        
        self.logger.info("Simple Data Capture stopped")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Simple TemperhUM Data Capture')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--data-file', help='Data file path')
    parser.add_argument('--mqtt-broker', help='MQTT broker address')
    parser.add_argument('--mqtt-port', type=int, help='MQTT broker port')
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    if args.data_file:
        CONFIG['data_file'] = args.data_file
    if args.mqtt_broker:
        CONFIG['mqtt_broker'] = args.mqtt_broker
    if args.mqtt_port:
        CONFIG['mqtt_port'] = args.mqtt_port
    
    # Create capture instance
    capture = SimpleDataCapture(debug=args.debug)
    
    try:
        capture.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 