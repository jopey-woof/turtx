# 🐢 Turtle Monitor API System

A lightweight, reliable API-based monitoring system for turtle enclosure sensors, designed to replace the WebSocket-based kiosk with a more stable HTTP polling architecture.

## 🏗️ Architecture Overview

### Hybrid System Design
- **Home Assistant**: Continues to run for smart plug control, mobile app, and automations
- **Custom API**: New lightweight FastAPI system for reliable kiosk display
- **MQTT Bridge**: Both systems receive sensor data in parallel
- **Zero Downtime**: Deploys alongside existing systems without disruption

### Data Flow
```
TEMPerHUM Sensors → MQTT Broker → Both Systems:
├── Home Assistant (existing functionality)
└── Custom API (new kiosk display)
```

## 📁 Project Structure

```
turtle-monitor/
├── api/                    # FastAPI server
│   ├── main.py            # Main API application
│   ├── Dockerfile         # Container configuration
│   └── requirements.txt   # Python dependencies
├── frontend/              # Kiosk display interface
│   └── index.html         # Turtle-themed touchscreen UI
├── config/                # Configuration files
│   └── mosquitto.conf     # MQTT broker configuration
├── deployment/            # Deployment scripts
│   ├── docker-compose.yml # Complete container stack
│   ├── deploy-turtle-api.sh # Remote deployment script
│   └── test-api.sh        # API testing script
└── README.md              # This file
```

## 🚀 Quick Start

### Local Development
1. **Clone the repository**:
   ```bash
   git clone https://github.com/jopey-woof/turtx.git
   cd turtx/turtle-monitor
   ```

2. **Test locally** (optional):
   ```bash
   cd deployment
   docker-compose up -d
   curl http://localhost:8000/api/health
   ```

3. **Deploy to remote system**:
   ```bash
   cd ../../
   ./deployment/remote-deploy.sh
   ```

### Remote Deployment
The system automatically deploys to the turtle monitoring system at `10.0.20.69`:

```bash
# One-command deployment
./deployment/remote-deploy.sh

# Or manual deployment
ssh turtle@10.0.20.69
cd /home/turtle/turtx
git pull origin main
cd turtle-monitor/deployment
./deploy-turtle-api.sh
```

## 🔧 API Endpoints

### Health Check
```http
GET /api/health
```
Returns system status, uptime, and component health.

### Latest Readings
```http
GET /api/latest
```
Returns current sensor readings with status assessment.

### Historical Data
```http
GET /api/history/{hours}
```
Returns historical data for the specified number of hours (1-168).

### Frontend Interface
```http
GET /
```
Serves the turtle-themed kiosk interface optimized for 1024×600 touchscreen.

## 📊 Sensor Data

### MQTT Topics
The API subscribes to both direct turtle topics and Home Assistant state topics:

**Direct Topics:**
- `turtle/sensors/sensor1/temperature` - Shell temperature
- `turtle/sensors/sensor1/humidity` - Shell humidity
- `turtle/sensors/sensor2/temperature` - Enclosure temperature
- `turtle/sensors/sensor2/humidity` - Enclosure humidity

**Home Assistant Topics:**
- `homeassistant/sensor/turtle_sensors_sensor1_temp/state`
- `homeassistant/sensor/turtle_sensors_sensor1_hum/state`
- `homeassistant/sensor/turtle_sensors_sensor2_temp/state`
- `homeassistant/sensor/turtle_sensors_sensor2_hum/state`

### Status Assessment
- **Shell Temperature**: Normal 70-90°F, Warning 65-95°F, Alert outside range
- **Enclosure Temperature**: Normal 70-85°F, Warning 65-90°F, Alert outside range
- **Humidity**: Normal 60-80%, Warning 50-85%, Alert outside range

## 🎨 Frontend Features

### Design
- **Theme**: Turtle shell patterns with earth tones
- **Colors**: Forest green, shell amber, warm brown, earth tan
- **Typography**: Large, readable fonts for touchscreen
- **Animations**: Subtle nature animations (shell movement, water ripples)

### Technical
- **Polling**: HTTP requests every 30 seconds (no WebSockets)
- **Error Handling**: Graceful offline mode with connection status
- **Performance**: Zero memory leaks, efficient DOM updates
- **Touch Optimization**: Large buttons, smooth interactions

### Display Elements
- **Shell Sensor Card**: Temperature and humidity with turtle shell icon
- **Enclosure Sensor Card**: Temperature and humidity with leaf/nature icon
- **Status Bar**: System status with last update timestamp
- **Offline Overlay**: Connection status when API unavailable

## 🐳 Docker Services

### turtle-api
- **Image**: Built from `api/` directory
- **Port**: 8000
- **Health Check**: `/api/health` endpoint
- **Volumes**: Database and frontend files

### mosquitto
- **Image**: `eclipse-mosquitto:2.0`
- **Ports**: 1883 (MQTT), 9001 (WebSocket)
- **Volumes**: Configuration, data, and logs

## 🔍 Testing

### API Testing
```bash
cd turtle-monitor/deployment
./test-api.sh
```

### Individual Tests
```bash
# API endpoints only
./test-api.sh --api-only

# MQTT connectivity only
./test-api.sh --mqtt-only

# System status only
./test-api.sh --status
```

### Manual Testing
```bash
# Test API health
curl http://10.0.20.69:8000/api/health

# Test sensor data
curl http://10.0.20.69:8000/api/latest

# Test frontend
curl http://10.0.20.69:8000/
```

## 🔧 Configuration

### Environment Variables
- `MQTT_BROKER`: MQTT broker host (default: localhost)
- `MQTT_PORT`: MQTT broker port (default: 1883)
- `DATABASE_PATH`: SQLite database path (default: /data/turtle_monitor.db)

### MQTT Configuration
The system uses the existing MQTT broker configuration from `config/mosquitto.conf`:
- Anonymous access enabled
- Persistence enabled
- WebSocket support on port 9001
- Comprehensive logging

## 📈 Performance

### Database
- **Storage**: SQLite with time-indexed sensor readings
- **Optimization**: Indexes on sensor_id and timestamp
- **Retention**: Configurable data retention (default: all data)

### Memory Usage
- **API Server**: ~50MB baseline
- **Frontend**: Zero memory leaks with HTTP polling
- **Database**: Efficient storage with automatic cleanup

### Reliability
- **MQTT Reconnection**: Automatic reconnection with exponential backoff
- **Error Handling**: Comprehensive logging and graceful failures
- **Health Checks**: Docker health checks for all services

## 🔄 Integration

### With Existing Systems
- **TEMPerHUM Service**: Continues running unchanged
- **Home Assistant**: Maintains all existing functionality
- **Kiosk Service**: Can be updated to point to new API

### Migration Strategy
1. **Phase 1**: Deploy API alongside existing system (zero downtime)
2. **Phase 2**: Test new kiosk display manually
3. **Phase 3**: Switch kiosk systemd service to new API
4. **Phase 4**: Validate 24+ hours of stable operation
5. **Phase 5**: Proceed with smart plug integration

## 🛠️ Troubleshooting

### Common Issues

**API not responding:**
```bash
# Check container status
docker ps | grep turtle-monitor

# Check container logs
docker logs turtle-monitor-api

# Test API directly
curl http://localhost:8000/api/health
```

**MQTT connection issues:**
```bash
# Check MQTT broker
docker logs turtle-monitor-mqtt

# Test MQTT connectivity
mosquitto_pub -h localhost -t test -m "test"
```

**Frontend not loading:**
```bash
# Check if frontend files are mounted
docker exec turtle-monitor-api ls -la /app/frontend

# Check API logs for frontend errors
docker logs turtle-monitor-api | grep -i frontend
```

### Logs
- **API Logs**: `docker logs turtle-monitor-api`
- **MQTT Logs**: `docker logs turtle-monitor-mqtt`
- **Deployment Logs**: `/tmp/turtle-deploy.log`

### Rollback
If issues occur, the system can be rolled back:
```bash
# Stop new containers
docker-compose -f turtle-monitor/deployment/docker-compose.yml down

# Restart original kiosk service
sudo systemctl restart kiosk
```

## 🚀 Next Steps

After the API system is validated and stable:

1. **Phase 4**: Smart plug integration via Home Assistant API
2. **Phase 5**: Camera feed integration
3. **Phase 6**: Advanced automations and mobile notifications

## 📝 License

This project is part of the Turtle Monitoring System and follows the same licensing terms as the main repository.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**🐢 Happy Turtle Monitoring! 🐢** 