#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import json
import os
from datetime import datetime

class StaticTurtleUpdater:
    def __init__(self):
        self.data = {
            'sensor1': {'temperature': None, 'humidity': None},
            'sensor2': {'temperature': None, 'humidity': None},
            'last_update': None
        }
        self.client = None
        self.html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Turtle Monitor</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #000; 
            color: #0f0; 
            margin: 20px;
            font-size: 24px;
        }
        .sensor { margin: 20px 0; }
        .value { font-size: 48px; font-weight: bold; }
        .status { color: #0f0; }
        .error { color: #f00; }
        .time { color: #666; font-size: 16px; margin-top: 40px; }
        .no-data { color: #666; }
    </style>
</head>
<body>
    <h1>🐢 Turtle Habitat Monitor</h1>
    <div class="status">Static Update - Refreshes every 30 seconds</div>
    
    <div class="sensor">
        <div>Sensor 1 Temperature: <span id="temp1" class="value">{temp1}</span>°C</div>
    </div>
    
    <div class="sensor">
        <div>Sensor 1 Humidity: <span id="hum1" class="value">{hum1}</span>%</div>
    </div>
    
    <div class="sensor">
        <div>Sensor 2 Temperature: <span id="temp2" class="value">{temp2}</span>°C</div>
    </div>
    
    <div class="sensor">
        <div>Sensor 2 Humidity: <span id="hum2" class="value">{hum2}</span>%</div>
    </div>
    
    <div class="time">Last Update: {last_update}</div>
    <div class="time">Next refresh in 30 seconds...</div>
</body>
</html>
'''
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"✅ Connected to MQTT broker with result code {rc}")
        client.subscribe('turtle/sensors/+/+')
        
    def on_message(self, client, userdata, msg):
        try:
            value = float(msg.payload.decode())
            topic = msg.topic
            
            if 'sensor1/temperature' in topic:
                self.data['sensor1']['temperature'] = value
            elif 'sensor1/humidity' in topic:
                self.data['sensor1']['humidity'] = value
            elif 'sensor2/temperature' in topic:
                self.data['sensor2']['temperature'] = value
            elif 'sensor2/humidity' in topic:
                self.data['sensor2']['humidity'] = value
                
            self.data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        except (ValueError, UnicodeDecodeError) as e:
            print(f"⚠️ Error processing message: {e}")
    
    def format_value(self, value):
        if value is None:
            return '<span class="no-data">--</span>'
        return f"{value:.1f}"
    
    def update_html(self):
        html_content = self.html_template.format(
            temp1=self.format_value(self.data['sensor1']['temperature']),
            hum1=self.format_value(self.data['sensor1']['humidity']),
            temp2=self.format_value(self.data['sensor2']['temperature']),
            hum2=self.format_value(self.data['sensor2']['humidity']),
            last_update=self.data['last_update'] or 'Never'
        )
        
        try:
            with open('/home/shrimp/turtle-dashboard/static.html', 'w') as f:
                f.write(html_content)
            print(f"📄 Updated static HTML at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Error writing HTML file: {e}")
    
    def run(self):
        print("🚀 Starting Static Turtle Monitor...")
        
        # Create MQTT client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, f"static-updater-{int(time.time())}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            # Connect to broker
            self.client.connect('localhost', 1883, 60)
            self.client.loop_start()
            
            # Initial update
            self.update_html()
            
            # Update every 30 seconds
            while True:
                time.sleep(30)
                self.update_html()
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()

if __name__ == "__main__":
    updater = StaticTurtleUpdater()
    updater.run() 