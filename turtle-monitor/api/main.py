#!/usr/bin/env python3
"""
🐢 Turtle Monitor API Server
FastAPI-based monitoring system for turtle enclosure sensors
"""

import os
import json
import sqlite3
import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi import Path
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "/data/turtle_monitor.db")

# MQTT Topics - Support both direct turtle topics and Home Assistant state topics
MQTT_TOPICS = [
    # Direct turtle sensor topics
    "turtle/sensors/sensor1/temperature",
    "turtle/sensors/sensor1/humidity", 
    "turtle/sensors/sensor2/temperature",
    "turtle/sensors/sensor2/humidity",
    "turtle/sensors/sensor1/availability",
    "turtle/sensors/sensor2/availability",
    # Home Assistant state topics (for compatibility)
    "homeassistant/sensor/turtle_sensors_sensor1_temp/state",
    "homeassistant/sensor/turtle_sensors_sensor1_hum/state",
    "homeassistant/sensor/turtle_sensors_sensor2_temp/state", 
    "homeassistant/sensor/turtle_sensors_sensor2_hum/state"
]

# Temperature ranges for status determination
SHELL_TEMP_RANGE = (70, 90)  # °F
ENCLOSURE_TEMP_RANGE = (70, 85)  # °F
HUMIDITY_RANGE = (60, 80)  # %

class SensorReading(BaseModel):
    """Pydantic model for sensor readings"""
    sensor_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    timestamp: datetime
    status: str = "unknown"

class SystemHealth(BaseModel):
    """Pydantic model for system health"""
    status: str
    uptime: float
    last_sensor_update: Optional[datetime] = None
    mqtt_connected: bool
    database_healthy: bool
    sensor_count: int

class TurtleMonitorAPI:
    """Main API class for turtle monitoring"""
    
    def __init__(self):
        self.mqtt_client = None
        self.db_conn = None
        self.start_time = time.time()
        self.last_sensor_update = None
        self.sensor_data = {}
        self.mqtt_connected = False
        
        # Initialize database
        self.init_database()
        
        # Setup MQTT client
        self.setup_mqtt()
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
            
            self.db_conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            cursor = self.db_conn.cursor()
            
            # Create sensor readings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id TEXT NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'unknown'
                )
            ''')
            
            # Create indexes for efficient queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
                ON sensor_readings(sensor_id, timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON sensor_readings(timestamp)
            ''')
            
            self.db_conn.commit()
            logger.info(f"Database initialized at {DATABASE_PATH}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def setup_mqtt(self):
        """Setup MQTT client and connection"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_message = self.on_mqtt_message
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            
            # Connect to MQTT broker
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            
            logger.info(f"MQTT client setup complete, connecting to {MQTT_BROKER}:{MQTT_PORT}")
            
        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.mqtt_connected = True
            logger.info("✅ Connected to MQTT broker")
            
            # Subscribe to all sensor topics
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
                logger.debug(f"Subscribed to {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.mqtt_connected = False
        logger.warning(f"Disconnected from MQTT broker, return code {rc}")
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"Received MQTT message: {topic} = {payload}")
            
            # Parse topic to extract sensor info
            parts = topic.split('/')
            
            # Handle turtle/sensors/ topics
            if len(parts) >= 4 and parts[0] == 'turtle' and parts[1] == 'sensors':
                sensor_id = parts[2]
                data_type = parts[3]
                
                # Update sensor data
                if sensor_id not in self.sensor_data:
                    self.sensor_data[sensor_id] = {}
                
                if data_type == 'temperature':
                    self.sensor_data[sensor_id]['temperature'] = float(payload)
                elif data_type == 'humidity':
                    self.sensor_data[sensor_id]['humidity'] = float(payload)
                elif data_type == 'availability':
                    self.sensor_data[sensor_id]['availability'] = payload
                
                # Store reading in database if we have both temp and humidity
                if ('temperature' in self.sensor_data[sensor_id] and 
                    'humidity' in self.sensor_data[sensor_id]):
                    
                    self.store_sensor_reading(sensor_id)
                    self.last_sensor_update = datetime.now()
            
            # Handle homeassistant/sensor/ topics
            elif len(parts) >= 5 and parts[0] == 'homeassistant' and parts[1] == 'sensor':
                # Extract sensor info from topic like "homeassistant/sensor/turtle_sensors_sensor1_temp/state"
                sensor_topic = parts[2]  # e.g., "turtle_sensors_sensor1_temp"
                
                # Parse sensor ID and type from the topic
                if '_temp' in sensor_topic:
                    sensor_id = sensor_topic.split('_')[-2]  # Extract sensor1 from turtle_sensors_sensor1_temp
                    data_type = 'temperature'
                elif '_hum' in sensor_topic:
                    sensor_id = sensor_topic.split('_')[-2]  # Extract sensor1 from turtle_sensors_sensor1_hum
                    data_type = 'humidity'
                else:
                    return  # Unknown sensor type
                
                # Update sensor data
                if sensor_id not in self.sensor_data:
                    self.sensor_data[sensor_id] = {}
                
                if data_type == 'temperature':
                    self.sensor_data[sensor_id]['temperature'] = float(payload)
                elif data_type == 'humidity':
                    self.sensor_data[sensor_id]['humidity'] = float(payload)
                
                # Store reading in database if we have both temp and humidity
                if ('temperature' in self.sensor_data[sensor_id] and 
                    'humidity' in self.sensor_data[sensor_id]):
                    
                    self.store_sensor_reading(sensor_id)
                    self.last_sensor_update = datetime.now()
            
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def store_sensor_reading(self, sensor_id: str):
        """Store sensor reading in database"""
        try:
            data = self.sensor_data[sensor_id]
            temperature = data.get('temperature')
            humidity = data.get('humidity')
            
            # Determine status based on temperature ranges
            status = self.determine_status(sensor_id, temperature, humidity)
            
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO sensor_readings (sensor_id, temperature, humidity, status)
                VALUES (?, ?, ?, ?)
            ''', (sensor_id, temperature, humidity, status))
            
            self.db_conn.commit()
            logger.debug(f"Stored reading for {sensor_id}: {temperature}°F, {humidity}%, status: {status}")
            
        except Exception as e:
            logger.error(f"Failed to store sensor reading: {e}")
    
    def determine_status(self, sensor_id: str, temperature: float, humidity: float) -> str:
        """Determine sensor status based on readings"""
        try:
            # Determine temperature range based on sensor
            if sensor_id == 'sensor1':  # Shell sensor
                temp_range = SHELL_TEMP_RANGE
            else:  # Enclosure sensor
                temp_range = ENCLOSURE_TEMP_RANGE
            
            # Check temperature
            if temperature < temp_range[0]:
                return "cold"
            elif temperature > temp_range[1]:
                return "hot"
            elif humidity < HUMIDITY_RANGE[0]:
                return "dry"
            elif humidity > HUMIDITY_RANGE[1]:
                return "humid"
            else:
                return "normal"
                
        except Exception as e:
            logger.error(f"Error determining status: {e}")
            return "unknown"
    
    def get_latest_readings(self) -> Dict[str, Any]:
        """Get latest sensor readings"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                SELECT sensor_id, temperature, humidity, timestamp, status
                FROM sensor_readings 
                WHERE timestamp = (
                    SELECT MAX(timestamp) 
                    FROM sensor_readings 
                    WHERE sensor_id = sensor_readings.sensor_id
                )
                ORDER BY sensor_id
            ''')
            
            readings = {}
            for row in cursor.fetchall():
                sensor_id, temp, hum, timestamp, status = row
                readings[sensor_id] = {
                    "temperature": temp,
                    "humidity": hum,
                    "timestamp": timestamp,
                    "status": status
                }
            
            return readings
            
        except Exception as e:
            logger.error(f"Failed to get latest readings: {e}")
            return {}
    
    def get_historical_data(self, hours: int) -> List[Dict[str, Any]]:
        """Get historical sensor data for last N hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor = self.db_conn.cursor()
            cursor.execute('''
                SELECT sensor_id, temperature, humidity, timestamp, status
                FROM sensor_readings
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            data = []
            for row in cursor.fetchall():
                sensor_id, temp, hum, timestamp, status = row
                data.append({
                    "sensor_id": sensor_id,
                    "temperature": temp,
                    "humidity": hum,
                    "timestamp": timestamp,
                    "status": status
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return []
    
    def get_system_health(self) -> SystemHealth:
        """Get system health information"""
        try:
            uptime = time.time() - self.start_time
            
            # Check database health
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sensor_readings")
            sensor_count = cursor.fetchone()[0]
            database_healthy = True
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            database_healthy = False
            sensor_count = 0
        
        return SystemHealth(
            status="healthy" if (self.mqtt_connected and database_healthy) else "degraded",
            uptime=uptime,
            last_sensor_update=self.last_sensor_update,
            mqtt_connected=self.mqtt_connected,
            database_healthy=database_healthy,
            sensor_count=sensor_count
        )
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            
            if self.db_conn:
                self.db_conn.close()
                
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Global API instance
api_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global api_instance
    
    # Startup
    logger.info("🐢 Starting Turtle Monitor API")
    api_instance = TurtleMonitorAPI()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Turtle Monitor API")
    if api_instance:
        api_instance.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Turtle Monitor API",
    description="FastAPI-based monitoring system for turtle enclosure sensors",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="/app/frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    try:
        with open("/app/frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>🐢 Turtle Monitor</h1><p>Frontend not found</p>")

@app.get("/api/health", response_model=SystemHealth)
async def health_check():
    """System health check endpoint"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    return api_instance.get_system_health()

@app.get("/api/latest")
async def get_latest_readings():
    """Get latest sensor readings"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    readings = api_instance.get_latest_readings()
    return {
        "timestamp": datetime.now().isoformat(),
        "readings": readings,
        "status": "online" if api_instance.mqtt_connected else "offline"
    }

@app.get("/api/history/{hours}")
async def get_historical_data(hours: int = Path(ge=1, le=168, description="Hours of history to retrieve (1-168)")):
    """Get historical sensor data"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    data = api_instance.get_historical_data(hours)
    return {
        "hours": hours,
        "data_points": len(data),
        "data": data
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 