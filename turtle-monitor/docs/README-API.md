# 🐢 Turtle Monitor API System

## Overview

The Turtle Monitor API is a FastAPI-based monitoring system designed to replace the problematic MQTT WebSocket kiosk display. This system provides a reliable, performant, and beautiful interface for monitoring turtle enclosure sensors without the memory leaks and connection issues associated with WebSocket implementations.

## System Architecture

### Hybrid Approach: API + Home Assistant

The Turtle Monitor API operates alongside the existing Home Assistant system, creating a robust dual-monitoring solution:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TEMPerHUM     │    │   MQTT Broker   │    │   Home Assistant│
│   Sensors       │───▶│   (Mosquitto)   │───▶│   (Existing)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Turtle Monitor │
                       │      API        │
                       │  (FastAPI)      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Frontend      │
                       │  (HTML/JS)      │
                       └─────────────────┘
```

### Key Components

1. **FastAPI Server** (`api/main.py`)
   - MQTT client for sensor data subscription
   - SQLite database for data storage
   - REST API endpoints
   - Static file serving

2. **Frontend Interface** (`frontend/index.html`)
   - Beautiful turtle-themed design
   - HTTP polling (no WebSockets)
   - Responsive 1024x600 touchscreen layout
   - Real-time status indicators

3. **MQTT Broker** (`config/mosquitto.conf`)
   - Eclipse Mosquitto 2.0
   - Optimized for turtle monitoring
   - WebSocket support for legacy compatibility

4. **Docker Orchestration** (`deployment/docker-compose.yml`)
   - Containerized deployment
   - Health checks and monitoring
   - Persistent data storage

## Migration Strategy

### Zero-Downtime Deployment

The Turtle Monitor API is designed for zero-downtime deployment alongside existing systems:

1. **Parallel Operation**: Both systems receive the same MQTT sensor data
2. **Independent Operation**: API system operates independently of Home Assistant
3. **Gradual Transition**: Kiosk can be pointed to new API when ready
4. **Easy Rollback**: Simple script-based rollback if needed

### Migration Steps

```bash
# 1. Deploy the new API system
cd turtle-monitor
./deployment/deploy-turtle-api.sh

# 2. Verify both systems are working
curl http://localhost:8000/api/health
curl http://localhost:8123/api/  # Home Assistant

# 3. Optionally update kiosk to use new API
# Edit kiosk configuration to point to http://localhost:8000
```

## API Endpoints

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "uptime": 3600.5,
  "last_sensor_update": "2024-01-15T10:30:00",
  "mqtt_connected": true,
  "database_healthy": true,
  "sensor_count": 150
}
```

### Latest Readings
```http
GET /api/latest
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "readings": {
    "sensor1": {
      "temperature": 75.2,
      "humidity": 68.5,
      "timestamp": "2024-01-15T10:30:00",
      "status": "normal"
    },
    "sensor2": {
      "temperature": 72.8,
      "humidity": 71.2,
      "timestamp": "2024-01-15T10:30:00",
      "status": "normal"
    }
  },
  "status": "online"
}
```

### Historical Data
```http
GET /api/history/{hours}
```

**Parameters:**
- `hours` (integer, 1-168): Number of hours of history to retrieve

**Response:**
```json
{
  "hours": 24,
  "data_points": 288,
  "data": [
    {
      "sensor_id": "sensor1",
      "temperature": 75.2,
      "humidity": 68.5,
      "timestamp": "2024-01-15T10:30:00",
      "status": "normal"
    }
  ]
}
```

## MQTT Topics

The API subscribes to the following MQTT topics:

| Topic | Description | Example Value |
|-------|-------------|---------------|
| `turtle/sensors/sensor1/temperature` | Shell temperature (°F) | `75.2` |
| `turtle/sensors/sensor1/humidity` | Shell humidity (%) | `68.5` |
| `turtle/sensors/sensor2/temperature` | Enclosure temperature (°F) | `72.8` |
| `turtle/sensors/sensor2/humidity` | Enclosure humidity (%) | `71.2` |
| `turtle/sensors/sensor1/availability` | Shell sensor status | `online` |
| `turtle/sensors/sensor2/availability` | Enclosure sensor status | `online` |

## Status Determination

The API automatically determines sensor status based on temperature and humidity ranges:

### Temperature Ranges
- **Shell Sensor**: 70-90°F (normal), 65-95°F (warning), <65°F or >95°F (alert)
- **Enclosure Sensor**: 70-85°F (normal), 65-90°F (warning), <65°F or >90°F (alert)

### Humidity Ranges
- **All Sensors**: 60-80% (normal), 50-85% (warning), <50% or >85% (alert)

### Status Values
- `normal`: All readings within optimal ranges
- `hot`: Temperature above maximum
- `cold`: Temperature below minimum
- `dry`: Humidity below minimum
- `humid`: Humidity above maximum

## Frontend Features

### Design Philosophy
- **Turtle-themed**: Organic shell patterns, earth tones, nature-inspired
- **Touch-optimized**: Large buttons, responsive design for 1024x600 screen
- **Performance-focused**: No memory leaks, efficient DOM updates
- **Reliable**: HTTP polling instead of WebSocket connections

### Key Features
- **Real-time Updates**: 30-second polling interval
- **Visual Status Indicators**: Color-coded readings and status dots
- **Offline Mode**: Graceful handling of connection loss
- **Responsive Design**: Adapts to different screen sizes
- **Smooth Animations**: Subtle turtle-themed animations

### Color Scheme
- **Shell Amber**: `#D4A574` - Primary accent color
- **Forest Green**: `#2D5016` - Background gradient
- **Warm Brown**: `#8B4513` - Secondary background
- **Success Green**: `#228B22` - Normal status
- **Warning Orange**: `#FF8C00` - Warning status
- **Alert Red**: `#DC143C` - Alert status

## Deployment

### Prerequisites
- Docker and Docker Compose
- Git repository access
- Port 8000 available
- Port 1883 available (or different MQTT port)

### Quick Deployment
```bash
# Clone repository
git clone <repository-url>
cd turtle-monitor

# Run deployment script
./deployment/deploy-turtle-api.sh
```

### Manual Deployment
```bash
# Build and start services
cd deployment
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

## Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_BROKER` | `localhost` | MQTT broker hostname |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `DATABASE_PATH` | `/data/turtle_monitor.db` | SQLite database path |

### Docker Compose Configuration
The system uses Docker Compose for orchestration with:
- **turtle-api**: FastAPI application
- **mosquitto**: MQTT broker
- **Persistent volumes**: Data and logs storage
- **Custom network**: Isolated communication

## Troubleshooting

### Common Issues

#### API Not Starting
```bash
# Check container logs
docker-compose logs turtle-api

# Verify port availability
netstat -tuln | grep 8000

# Check Docker resources
docker system df
```

#### MQTT Connection Issues
```bash
# Test MQTT connectivity
docker exec turtle-monitor-mqtt mosquitto_pub -h localhost -t test -m "test"

# Check MQTT logs
docker-compose logs mosquitto

# Verify MQTT configuration
docker exec turtle-monitor-mqtt cat /mosquitto/config/mosquitto.conf
```

#### Frontend Not Loading
```bash
# Check if frontend files are mounted
docker exec turtle-monitor-api ls -la /app/frontend

# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/

# Check browser console for JavaScript errors
```

#### Database Issues
```bash
# Check database file
docker exec turtle-monitor-api ls -la /data/

# Verify database integrity
docker exec turtle-monitor-api sqlite3 /data/turtle_monitor.db "PRAGMA integrity_check;"

# Check database size
docker exec turtle-monitor-api sqlite3 /data/turtle_monitor.db "SELECT COUNT(*) FROM sensor_readings;"
```

### Performance Monitoring

#### Memory Usage
```bash
# Monitor container memory
docker stats turtle-monitor-api

# Check for memory leaks
docker exec turtle-monitor-api ps aux
```

#### Database Performance
```bash
# Check database size
docker exec turtle-monitor-api sqlite3 /data/turtle_monitor.db "SELECT COUNT(*) FROM sensor_readings;"

# Analyze query performance
docker exec turtle-monitor-api sqlite3 /data/turtle_monitor.db "ANALYZE;"
```

### Log Analysis
```bash
# View API logs
docker-compose logs -f turtle-api

# View MQTT logs
docker-compose logs -f mosquitto

# Search for errors
docker-compose logs | grep -i error
```

## Benefits Over WebSocket Approach

### Reliability
- **No Connection Drops**: HTTP polling is more reliable than WebSocket connections
- **Automatic Recovery**: Failed requests automatically retry
- **Graceful Degradation**: System continues working with intermittent connectivity

### Performance
- **No Memory Leaks**: Simple HTTP requests don't accumulate memory
- **Efficient Resource Usage**: Minimal CPU and memory overhead
- **Predictable Behavior**: Consistent performance over time

### Maintainability
- **Simple Architecture**: Easy to understand and debug
- **Standard Protocols**: Uses well-established HTTP/REST patterns
- **Easy Monitoring**: Standard HTTP health checks and metrics

### Compatibility
- **Works Everywhere**: HTTP works in all environments
- **No Special Requirements**: No WebSocket support needed
- **Firewall Friendly**: Standard HTTP ports only

## Maintenance

### Regular Tasks
- **Log Rotation**: Monitor log file sizes
- **Database Cleanup**: Archive old sensor data
- **Backup Verification**: Test backup restoration
- **Security Updates**: Keep Docker images updated

### Backup Strategy
```bash
# Create manual backup
tar -czf backup-$(date +%Y%m%d).tar.gz /home/turtle/turtle-monitor/data/

# Restore from backup
tar -xzf backup-20240115.tar.gz -C /home/turtle/turtle-monitor/
```

### Updates
```bash
# Update system
git pull
docker-compose down
docker-compose up -d --build

# Verify update
curl http://localhost:8000/api/health
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review container logs for error messages
3. Verify configuration files
4. Test individual components
5. Check system resources

The Turtle Monitor API provides a robust, reliable, and beautiful solution for turtle enclosure monitoring that eliminates the issues associated with WebSocket-based implementations while maintaining full compatibility with existing Home Assistant systems. 