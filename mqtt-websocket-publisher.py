#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import random

# MQTT broker configuration
broker = "localhost"
port = 1883
client_id = f"turtle-publisher-{random.randint(1000, 9999)}"

# Topics
topics = [
    "turtle/sensor1/temperature",
    "turtle/sensor1/humidity",
    "turtle/sensor2/temperature", 
    "turtle/sensor2/humidity"
]

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ Connected to MQTT broker with result code {rc}")
    
def on_publish(client, userdata, mid, reason_code=None, properties=None):
    print(f"📤 Message published with ID {mid}")

# Create client with v2 API
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id)
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to broker
client.connect(broker, port, 60)

# Start the loop
client.loop_start()

# Publish test data
print("🐢 Publishing turtle sensor data...")

# Sensor 1 data
temp1 = round(random.uniform(24.0, 28.0), 1)
hum1 = round(random.uniform(65.0, 75.0), 1)

# Sensor 2 data  
temp2 = round(random.uniform(25.0, 29.0), 1)
hum2 = round(random.uniform(68.0, 78.0), 1)

# Publish all sensor data
data = [
    ("turtle/sensor1/temperature", str(temp1)),
    ("turtle/sensor1/humidity", str(hum1)),
    ("turtle/sensor2/temperature", str(temp2)),
    ("turtle/sensor2/humidity", str(hum2))
]

for topic, message in data:
    result = client.publish(topic, message)
    print(f"📡 {topic}: {message}")
    time.sleep(0.5)

print("✅ All sensor data published!")
client.loop_stop()
client.disconnect() 