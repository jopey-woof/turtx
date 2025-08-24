#!/usr/bin/env python3
"""
🐢 Turtle Monitor API Server
FastAPI-based monitoring system for turtle enclosure sensors with camera integration
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
from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from fastapi import Path
import uvicorn

# Import camera routes
from camera_routes import camera_router, init_camera_manager, stop_camera_manager

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
            
            # Create index for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
                ON sensor_readings(sensor_id, timestamp)
            ''')
            
            self.db_conn.commit()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
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
            
            logger.info(f"✅ MQTT client setup complete - connecting to {MQTT_BROKER}:{MQTT_PORT}")
            
        except Exception as e:
            logger.error(f"❌ MQTT setup failed: {e}")
            raise
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("✅ Connected to MQTT broker")
            self.mqtt_connected = True
            
            # Subscribe to all sensor topics
            for topic in MQTT_TOPICS:
                client.subscribe(topic)
                logger.info(f"📡 Subscribed to: {topic}")
        else:
            logger.error(f"❌ MQTT connection failed with code: {rc}")
            self.mqtt_connected = False
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.warning(f"⚠️ MQTT disconnected with code: {rc}")
        self.mqtt_connected = False
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # Parse sensor data based on topic
            if "temperature" in topic:
                self.process_temperature_reading(topic, float(payload))
            elif "humidity" in topic:
                self.process_humidity_reading(topic, float(payload))
            elif "availability" in topic:
                self.process_availability_reading(topic, payload)
            
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")
    
    def process_temperature_reading(self, topic: str, temperature: float):
        """Process temperature reading from MQTT"""
        try:
            # Extract sensor ID from topic
            if "sensor1" in topic:
                sensor_id = "sensor1"
            elif "sensor2" in topic:
                sensor_id = "sensor2"
            else:
                sensor_id = "unknown"
            
            # Store in memory
            if sensor_id not in self.sensor_data:
                self.sensor_data[sensor_id] = {}
            
            self.sensor_data[sensor_id]['temperature'] = temperature
            self.sensor_data[sensor_id]['timestamp'] = datetime.now()
            
            # Store in database
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO sensor_readings (sensor_id, temperature, timestamp)
                VALUES (?, ?, ?)
            ''', (sensor_id, temperature, datetime.now()))
            self.db_conn.commit()
            
            self.last_sensor_update = datetime.now()
            logger.debug(f"🌡️ Temperature reading: {sensor_id} = {temperature}°F")
            
        except Exception as e:
            logger.error(f"❌ Error processing temperature reading: {e}")
    
    def process_humidity_reading(self, topic: str, humidity: float):
        """Process humidity reading from MQTT"""
        try:
            # Extract sensor ID from topic
            if "sensor1" in topic:
                sensor_id = "sensor1"
            elif "sensor2" in topic:
                sensor_id = "sensor2"
            else:
                sensor_id = "unknown"
            
            # Store in memory
            if sensor_id not in self.sensor_data:
                self.sensor_data[sensor_id] = {}
            
            self.sensor_data[sensor_id]['humidity'] = humidity
            self.sensor_data[sensor_id]['timestamp'] = datetime.now()
            
            # Store in database
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO sensor_readings (sensor_id, humidity, timestamp)
                VALUES (?, ?, ?)
            ''', (sensor_id, humidity, datetime.now()))
            self.db_conn.commit()
            
            self.last_sensor_update = datetime.now()
            logger.debug(f"💧 Humidity reading: {sensor_id} = {humidity}%")
            
        except Exception as e:
            logger.error(f"❌ Error processing humidity reading: {e}")
    
    def process_availability_reading(self, topic: str, status: str):
        """Process sensor availability reading from MQTT"""
        try:
            # Extract sensor ID from topic
            if "sensor1" in topic:
                sensor_id = "sensor1"
            elif "sensor2" in topic:
                sensor_id = "sensor2"
            else:
                sensor_id = "unknown"
            
            # Store in memory
            if sensor_id not in self.sensor_data:
                self.sensor_data[sensor_id] = {}
            
            self.sensor_data[sensor_id]['status'] = status
            self.sensor_data[sensor_id]['timestamp'] = datetime.now()
            
            logger.debug(f"📡 Sensor status: {sensor_id} = {status}")
            
        except Exception as e:
            logger.error(f"❌ Error processing availability reading: {e}")
    
    def get_latest_readings(self) -> Dict[str, Any]:
        """Get latest sensor readings with status"""
        readings = {}
        
        for sensor_id, data in self.sensor_data.items():
            if 'timestamp' in data:
                # Determine status based on temperature and humidity
                status = self.determine_sensor_status(sensor_id, data)
                
                readings[sensor_id] = {
                    'temperature': data.get('temperature'),
                    'humidity': data.get('humidity'),
                    'timestamp': data['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'status': status
                }
        
        return readings
    
    def determine_sensor_status(self, sensor_id: str, data: Dict[str, Any]) -> str:
        """Determine sensor status based on readings"""
        try:
            temp = data.get('temperature')
            humidity = data.get('humidity')
            
            if temp is None and humidity is None:
                return "unknown"
            
            # Check temperature ranges
            if temp is not None:
                if sensor_id == "sensor1":  # Shell temperature
                    if temp < SHELL_TEMP_RANGE[0]:
                        return "cold"
                    elif temp > SHELL_TEMP_RANGE[1]:
                        return "hot"
                else:  # Enclosure temperature
                    if temp < ENCLOSURE_TEMP_RANGE[0]:
                        return "cold"
                    elif temp > ENCLOSURE_TEMP_RANGE[1]:
                        return "hot"
            
            # Check humidity
            if humidity is not None:
                if humidity < HUMIDITY_RANGE[0]:
                    return "dry"
                elif humidity > HUMIDITY_RANGE[1]:
                    return "wet"
            
            return "normal"
            
        except Exception as e:
            logger.error(f"❌ Error determining sensor status: {e}")
            return "unknown"
    
    def get_historical_data(self, hours: int) -> List[Dict[str, Any]]:
        """Get historical sensor data from database"""
        try:
            cursor = self.db_conn.cursor()
            
            # Get data from the last N hours
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT sensor_id, temperature, humidity, timestamp, status
                FROM sensor_readings
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                data.append({
                    'sensor_id': row[0],
                    'temperature': row[1],
                    'humidity': row[2],
                    'timestamp': row[3],
                    'status': row[4] or 'unknown'
                })
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error getting historical data: {e}")
            return []
    
    def get_system_health(self) -> SystemHealth:
        """Get system health information"""
        try:
            uptime = time.time() - self.start_time
            sensor_count = len(self.sensor_data)
            
            # Check database health
            db_healthy = False
            if self.db_conn:
                try:
                    cursor = self.db_conn.cursor()
                    cursor.execute("SELECT 1")
                    db_healthy = True
                except:
                    db_healthy = False
            
            return SystemHealth(
                status="healthy" if self.mqtt_connected and db_healthy else "degraded",
                uptime=uptime,
                last_sensor_update=self.last_sensor_update,
                mqtt_connected=self.mqtt_connected,
                database_healthy=db_healthy,
                sensor_count=sensor_count
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting system health: {e}")
            return SystemHealth(
                status="error",
                uptime=time.time() - self.start_time,
                mqtt_connected=False,
                database_healthy=False,
                sensor_count=0
            )
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                logger.info("📡 MQTT client disconnected")
            
            if self.db_conn:
                self.db_conn.close()
                logger.info("🗄️ Database connection closed")
                
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

# Global API instance
api_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global api_instance
    
    # Startup
    logger.info("🐢 Starting Turtle Monitor API with Camera Integration")
    api_instance = TurtleMonitorAPI()
    
    # Initialize camera manager
    try:
        init_camera_manager()
        logger.info("📹 Camera manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize camera manager: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Turtle Monitor API")
    if api_instance:
        api_instance.cleanup()
    
    # Stop camera manager
    try:
        stop_camera_manager()
        logger.info("📹 Camera manager stopped")
    except Exception as e:
        logger.error(f"Error stopping camera manager: {e}")

# Create FastAPI app
app = FastAPI(
    title="Turtle Monitor API",
    description="FastAPI-based monitoring system for turtle enclosure sensors with camera integration",
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
app.mount("/static", StaticFiles(directory="/home/shrimp/turtx/turtle-monitor/frontend"), name="static")

# Include camera routes
app.include_router(camera_router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    try:
        with open("/home/shrimp/turtx/turtle-monitor/frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>🐢 Turtle Monitor</h1><p>Frontend not found</p>")

@app.get("/health")
async def health():
    """Simple health check endpoint"""
    return "healthy"

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

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Test endpoint working"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 