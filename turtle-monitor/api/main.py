#!/usr/bin/env python3
"""
🐢 Turtle Monitor API Server
FastAPI-based monitoring system for turtle enclosure sensors with camera integration
Enhanced with robust sensor connection monitoring and alerting
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
from enum import Enum

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
DATABASE_PATH = os.getenv("DATABASE_PATH", "/home/shrimp/turtx/turtle-monitor/api/data/turtle_monitor.db")

# Sensor connection monitoring constants
SENSOR_TIMEOUT_SECONDS = 30  # Consider sensor offline after 30 seconds without data
CONNECTION_CHECK_INTERVAL = 10  # Check connections every 10 seconds
ALERT_COOLDOWN_MINUTES = 5  # Don't spam alerts

class SensorStatus(Enum):
    """Sensor status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"

class ConnectionAlert(BaseModel):
    """Pydantic model for connection alerts"""
    sensor_id: str
    alert_type: str  # "connection_lost", "connection_restored", "data_stale"
    message: str
    timestamp: datetime
    severity: str  # "critical", "warning", "info"

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

class SensorHealth(BaseModel):
    """Pydantic model for sensor health"""
    sensor_id: str
    status: SensorStatus
    last_seen: Optional[datetime] = None
    connection_uptime: Optional[float] = None
    data_freshness_seconds: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None
    alerts: List[ConnectionAlert] = []

class SystemHealth(BaseModel):
    """Pydantic model for system health"""
    status: str
    uptime: float
    last_sensor_update: Optional[datetime] = None
    mqtt_connected: bool
    database_healthy: bool
    sensor_count: int
    sensor_health: Dict[str, SensorHealth]
    connection_alerts: List[ConnectionAlert]
    overall_health: str  # "healthy", "degraded", "critical"

class TurtleMonitorAPI:
    """Main API class for turtle monitoring with enhanced connection monitoring"""
    
    def __init__(self):
        self.mqtt_client = None
        self.db_conn = None
        self.start_time = time.time()
        self.last_sensor_update = None
        self.sensor_data = {}
        self.mqtt_connected = False
        
        # Enhanced sensor monitoring
        self.sensor_health = {}
        self.connection_alerts = []
        self.last_alert_time = {}
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Initialize database
        self.init_database()
        
        # Setup MQTT client
        self.setup_mqtt()
        
        # Start connection monitoring
        self.start_connection_monitoring()
    
    def init_database(self):
        """Initialize SQLite database with enhanced tables"""
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
            
            # Create connection alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connection_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create sensor health history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_health_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data_freshness_seconds REAL,
                    error_count INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_sensor_timestamp 
                ON sensor_readings(sensor_id, timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                ON connection_alerts(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_health_timestamp 
                ON sensor_health_history(timestamp)
            ''')
            
            self.db_conn.commit()
            logger.info("✅ Enhanced database initialized successfully")
            
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
    
    def start_connection_monitoring(self):
        """Start background thread for connection monitoring"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._connection_monitor_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("🔍 Connection monitoring started")
    
    def _connection_monitor_loop(self):
        """Background loop for monitoring sensor connections"""
        while self.monitoring_active:
            try:
                self._check_sensor_connections()
                time.sleep(CONNECTION_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"❌ Error in connection monitoring loop: {e}")
                time.sleep(CONNECTION_CHECK_INTERVAL)
    
    def _check_sensor_connections(self):
        """Check all sensor connections and update health status"""
        current_time = datetime.now()
        
        for sensor_id in ["sensor1", "sensor2"]:
            # Initialize sensor health if not exists
            if sensor_id not in self.sensor_health:
                self.sensor_health[sensor_id] = SensorHealth(
                    sensor_id=sensor_id,
                    status=SensorStatus.UNKNOWN,
                    error_count=0
                )
            
            sensor_data = self.sensor_data.get(sensor_id, {})
            health = self.sensor_health[sensor_id]
            
            # Check if sensor has recent data
            if 'timestamp' in sensor_data:
                time_since_last = (current_time - sensor_data['timestamp']).total_seconds()
                health.data_freshness_seconds = time_since_last
                
                if time_since_last <= SENSOR_TIMEOUT_SECONDS:
                    # Sensor is online
                    if health.status != SensorStatus.ONLINE:
                        health.status = SensorStatus.ONLINE
                        health.last_seen = current_time
                        if health.connection_uptime is None:
                            health.connection_uptime = 0
                        else:
                            health.connection_uptime += CONNECTION_CHECK_INTERVAL
                        
                        # Alert if sensor came back online
                        self._create_alert(sensor_id, "connection_restored", 
                                         f"Sensor {sensor_id} connection restored", "info")
                        logger.info(f"✅ Sensor {sensor_id} connection restored")
                else:
                    # Sensor data is stale
                    if health.status == SensorStatus.ONLINE:
                        health.status = SensorStatus.DEGRADED
                        self._create_alert(sensor_id, "data_stale", 
                                         f"Sensor {sensor_id} data is stale ({time_since_last:.1f}s)", "warning")
                        logger.warning(f"⚠️ Sensor {sensor_id} data is stale ({time_since_last:.1f}s)")
                    
                    if time_since_last > SENSOR_TIMEOUT_SECONDS * 2:
                        # Sensor is offline
                        if health.status != SensorStatus.OFFLINE:
                            health.status = SensorStatus.OFFLINE
                            health.connection_uptime = 0
                            self._create_alert(sensor_id, "connection_lost", 
                                             f"Sensor {sensor_id} connection lost", "critical")
                            logger.error(f"❌ Sensor {sensor_id} connection lost")
            else:
                # No data ever received
                if health.status != SensorStatus.UNKNOWN:
                    health.status = SensorStatus.UNKNOWN
                    self._create_alert(sensor_id, "no_data", 
                                     f"Sensor {sensor_id} has never sent data", "critical")
                    logger.error(f"❌ Sensor {sensor_id} has never sent data")
            
            # Store health history
            self._store_health_history(sensor_id, health)
    
    def _create_alert(self, sensor_id: str, alert_type: str, message: str, severity: str):
        """Create and store a connection alert"""
        current_time = datetime.now()
        
        # Check alert cooldown
        alert_key = f"{sensor_id}_{alert_type}"
        if alert_key in self.last_alert_time:
            time_since_last = (current_time - self.last_alert_time[alert_key]).total_seconds()
            if time_since_last < ALERT_COOLDOWN_MINUTES * 60:
                return  # Skip alert due to cooldown
        
        # Create alert
        alert = ConnectionAlert(
            sensor_id=sensor_id,
            alert_type=alert_type,
            message=message,
            timestamp=current_time,
            severity=severity
        )
        
        # Store alert
        self.connection_alerts.append(alert)
        self.last_alert_time[alert_key] = current_time
        
        # Keep only recent alerts (last 24 hours)
        cutoff_time = current_time - timedelta(hours=24)
        self.connection_alerts = [a for a in self.connection_alerts if a.timestamp > cutoff_time]
        
        # Store in database
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO connection_alerts (sensor_id, alert_type, message, severity, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (sensor_id, alert_type, message, severity, current_time))
            self.db_conn.commit()
        except Exception as e:
            logger.error(f"❌ Error storing alert in database: {e}")
        
        # Log alert
        log_level = logging.ERROR if severity == "critical" else logging.WARNING if severity == "warning" else logging.INFO
        logger.log(log_level, f"🚨 {message}")
    
    def _store_health_history(self, sensor_id: str, health: SensorHealth):
        """Store sensor health history in database"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO sensor_health_history (sensor_id, status, data_freshness_seconds, error_count, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (sensor_id, health.status.value, health.data_freshness_seconds, health.error_count, datetime.now()))
            self.db_conn.commit()
        except Exception as e:
            logger.error(f"❌ Error storing health history: {e}")
    
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
            self._increment_sensor_error(sensor_id, str(e))
    
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
            self._increment_sensor_error(sensor_id, str(e))
    
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
            self._increment_sensor_error(sensor_id, str(e))
    
    def _increment_sensor_error(self, sensor_id: str, error_message: str):
        """Increment error count for a sensor"""
        if sensor_id not in self.sensor_health:
            self.sensor_health[sensor_id] = SensorHealth(
                sensor_id=sensor_id,
                status=SensorStatus.ERROR,
                error_count=0
            )
        
        self.sensor_health[sensor_id].error_count += 1
        self.sensor_health[sensor_id].last_error = error_message
        
        # Update status to error if too many errors
        if self.sensor_health[sensor_id].error_count > 5:
            self.sensor_health[sensor_id].status = SensorStatus.ERROR
    
    def get_latest_readings(self) -> Dict[str, Any]:
        """Get latest sensor readings with enhanced status"""
        readings = {}
        
        for sensor_id, data in self.sensor_data.items():
            if 'timestamp' in data:
                # Determine status based on temperature and humidity
                status = self.determine_sensor_status(sensor_id, data)
                
                # Get health information
                health = self.sensor_health.get(sensor_id, SensorHealth(
                    sensor_id=sensor_id,
                    status=SensorStatus.UNKNOWN
                ))
                
                readings[sensor_id] = {
                    'temperature': data.get('temperature'),
                    'humidity': data.get('humidity'),
                    'timestamp': data['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'status': status,
                    'connection_status': health.status.value,
                    'data_freshness_seconds': health.data_freshness_seconds,
                    'error_count': health.error_count
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
    
    def get_connection_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent connection alerts"""
        try:
            cursor = self.db_conn.cursor()
            
            # Get alerts from the last N hours
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT sensor_id, alert_type, message, severity, timestamp
                FROM connection_alerts
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT 100
            ''', (cutoff_time,))
            
            rows = cursor.fetchall()
            
            alerts = []
            for row in rows:
                alerts.append({
                    'sensor_id': row[0],
                    'alert_type': row[1],
                    'message': row[2],
                    'severity': row[3],
                    'timestamp': row[4]
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error getting connection alerts: {e}")
            return []
    
    def get_system_health(self) -> SystemHealth:
        """Get enhanced system health information"""
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
            
            # Determine overall health
            critical_alerts = [a for a in self.connection_alerts if a.severity == "critical"]
            warning_alerts = [a for a in self.connection_alerts if a.severity == "warning"]
            
            if critical_alerts:
                overall_health = "critical"
            elif warning_alerts or not self.mqtt_connected or not db_healthy:
                overall_health = "degraded"
            else:
                overall_health = "healthy"
            
            return SystemHealth(
                status=overall_health,
                uptime=uptime,
                last_sensor_update=self.last_sensor_update,
                mqtt_connected=self.mqtt_connected,
                database_healthy=db_healthy,
                sensor_count=sensor_count,
                sensor_health=self.sensor_health,
                connection_alerts=self.connection_alerts,
                overall_health=overall_health
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting system health: {e}")
            return SystemHealth(
                status="error",
                uptime=time.time() - self.start_time,
                mqtt_connected=False,
                database_healthy=False,
                sensor_count=0,
                sensor_health={},
                connection_alerts=[],
                overall_health="error"
            )
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop monitoring
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
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

# Mount static files (commented out - serving through nginx)
app.mount("/static", StaticFiles(directory="/app/frontend"), name="static")

# Include camera routes
app.include_router(camera_router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    try:
        with open("/app/frontend/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        try:
            # Fallback to host path
            with open("/home/shrimp/turtx/turtle-monitor/frontend/index.html", "r") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse(content="<h1>🐢 Turtle Monitor</h1><p>Frontend not found</p>")

@app.get("/css/{filename}")
async def serve_css(filename: str):
    """Serve CSS files"""
    try:
        return FileResponse(f"/home/shrimp/turtx/turtle-monitor/frontend/css/{filename}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSS file not found")

@app.get("/js/{filename}")
async def serve_js(filename: str):
    """Serve JavaScript files"""
    try:
        return FileResponse(f"/home/shrimp/turtx/turtle-monitor/frontend/js/{filename}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JavaScript file not found")

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

@app.get("/api/sensor-health")
async def get_sensor_health():
    """Get detailed sensor health information"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "sensor_health": api_instance.sensor_health,
        "overall_health": api_instance.get_system_health().overall_health
    }

@app.get("/api/connection-alerts")
async def get_connection_alerts(hours: int = 24):
    """Get recent connection alerts"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    alerts = api_instance.get_connection_alerts(hours)
    return {
        "timestamp": datetime.now().isoformat(),
        "hours": hours,
        "alert_count": len(alerts),
        "alerts": alerts
    }

@app.get("/api/sensor-status/{sensor_id}")
async def get_sensor_status(sensor_id: str):
    """Get detailed status for a specific sensor"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    if sensor_id not in api_instance.sensor_health:
        raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} not found")
    
    health = api_instance.sensor_health[sensor_id]
    sensor_data = api_instance.sensor_data.get(sensor_id, {})
    
    return {
        "sensor_id": sensor_id,
        "timestamp": datetime.now().isoformat(),
        "health": {
            "status": health.status.value,
            "last_seen": health.last_seen.isoformat() if health.last_seen else None,
            "connection_uptime": health.connection_uptime,
            "data_freshness_seconds": health.data_freshness_seconds,
            "error_count": health.error_count,
            "last_error": health.last_error
        },
        "data": {
            "temperature": sensor_data.get('temperature'),
            "humidity": sensor_data.get('humidity'),
            "last_update": sensor_data.get('timestamp').isoformat() if 'timestamp' in sensor_data else None
        }
    }

@app.get("/api/system-status")
async def get_system_status():
    """Get comprehensive system status including all sensors and alerts"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    health = api_instance.get_system_health()
    readings = api_instance.get_latest_readings()
    alerts = api_instance.get_connection_alerts(24)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "status": health.overall_health,
            "uptime_seconds": health.uptime,
            "mqtt_connected": health.mqtt_connected,
            "database_healthy": health.database_healthy,
            "sensor_count": health.sensor_count
        },
        "sensors": readings,
        "alerts": {
            "total": len(alerts),
            "critical": len([a for a in alerts if a['severity'] == 'critical']),
            "warning": len([a for a in alerts if a['severity'] == 'warning']),
            "info": len([a for a in alerts if a['severity'] == 'info']),
            "recent": alerts[:10]  # Last 10 alerts
        }
    }

@app.get("/api/health-check")
async def comprehensive_health_check():
    """Comprehensive health check for monitoring systems"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API not initialized")
    
    health = api_instance.get_system_health()
    
    # Check for critical issues
    critical_issues = []
    warning_issues = []
    
    if not health.mqtt_connected:
        critical_issues.append("MQTT connection lost")
    
    if not health.database_healthy:
        critical_issues.append("Database connection failed")
    
    # Check sensor status
    for sensor_id, sensor_health in health.sensor_health.items():
        if sensor_health.status == SensorStatus.OFFLINE:
            critical_issues.append(f"Sensor {sensor_id} is offline")
        elif sensor_health.status == SensorStatus.DEGRADED:
            warning_issues.append(f"Sensor {sensor_id} data is stale")
        elif sensor_health.status == SensorStatus.ERROR:
            critical_issues.append(f"Sensor {sensor_id} has errors")
    
    # Determine overall status
    if critical_issues:
        status = "critical"
    elif warning_issues:
        status = "warning"
    else:
        status = "healthy"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "critical_issues": critical_issues,
        "warning_issues": warning_issues,
        "uptime_seconds": health.uptime,
        "sensor_count": health.sensor_count,
        "mqtt_connected": health.mqtt_connected,
        "database_healthy": health.database_healthy
    }

@app.get("/api/direct-sensors")
async def get_direct_sensor_readings():
    """Get sensor readings directly from hardware, bypassing MQTT"""
    try:
        # Import the sensor controller
        from temperhum_controller import TemperhUMController
        
        # Initialize controller
        controller = TemperhUMController(verbose=False)
        
        # Read all sensors
        readings = controller.read_all_sensors()
        
        # Format the response
        formatted_readings = {}
        for sensor_id, data in readings.items():
            if data and 'internal_temperature_f' in data and 'internal_humidity' in data:
                formatted_readings[sensor_id] = {
                    "temperature": round(data['internal_temperature_f'], 1),
                    "humidity": round(data['internal_humidity'], 1),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "online",
                    "source": "direct_hardware"
                }
            else:
                formatted_readings[sensor_id] = {
                    "temperature": None,
                    "humidity": None,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "error",
                    "source": "direct_hardware",
                    "error": "Invalid sensor data"
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "readings": formatted_readings,
            "source": "direct_hardware"
        }
        
    except Exception as e:
        logger.error(f"Error reading sensors directly: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading sensors: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 