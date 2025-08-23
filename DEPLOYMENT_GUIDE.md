# 🐢 Turtle Monitor API Deployment Guide

## Overview

The API-based kiosk system is now ready for deployment! This system provides a reliable, beautiful interface for monitoring turtle enclosure sensors without the memory leaks and stability issues of the previous WebSocket implementation.

## 🚀 Quick Deployment

### Option 1: One-Command Deployment (Recommended)
```bash
# From the turtx directory
./deployment/remote-deploy.sh
```

This script will:
1. Commit and push any local changes to GitHub
2. SSH to the remote turtle system
3. Pull the latest changes
4. Deploy the API system
5. Provide status information

### Option 2: Manual Deployment
```bash
# SSH to the remote system
ssh turtle@10.0.20.69

# Navigate to project and pull changes
cd /home/turtle/turtx
git pull origin main

# Deploy the API system
cd turtle-monitor/deployment
./deploy-turtle-api.sh
```

## 🔍 Testing the Deployment

### Test API Endpoints
```bash
# Health check
curl http://10.0.20.69:8000/api/health

# Latest sensor readings
curl http://10.0.20.69:8000/api/latest

# Frontend interface
curl http://10.0.20.69:8000/
```

### Run Comprehensive Tests
```bash
# SSH to remote system
ssh turtle@10.0.20.69

# Run test script
cd /home/turtle/turtx/turtle-monitor/deployment
./test-api.sh
```

## 🎯 What's New

### API-Based Architecture
- **FastAPI Server**: Lightweight, high-performance API
- **HTTP Polling**: 30-second polling instead of WebSockets
- **SQLite Database**: Local storage of sensor readings
- **MQTT Integration**: Subscribes to existing TEMPerHUM topics

### Beautiful Frontend
- **Turtle Theme**: Shell patterns, earth tones, nature animations
- **Touch Optimized**: Perfect for 1024×600 kiosk display
- **Status Indicators**: Visual alerts for temperature/humidity ranges
- **Offline Mode**: Graceful handling of connection issues

### Zero Downtime Deployment
- **Parallel Operation**: Runs alongside existing Home Assistant
- **Non-Destructive**: Doesn't affect current TEMPerHUM service
- **Easy Rollback**: Simple script to revert if needed

## 📊 System Status

### API Endpoints
- **Health**: `http://10.0.20.69:8000/api/health`
- **Latest Data**: `http://10.0.20.69:8000/api/latest`
- **Historical Data**: `http://10.0.20.69:8000/api/history/24`
- **Frontend**: `http://10.0.20.69:8000/`

### Docker Services
- **turtle-monitor-api**: FastAPI server on port 8000
- **turtle-monitor-mqtt**: MQTT broker on ports 1883/9001

### MQTT Topics
The API subscribes to:
- `turtle/sensors/sensor1/temperature` (Shell temperature)
- `turtle/sensors/sensor1/humidity` (Shell humidity)
- `turtle/sensors/sensor2/temperature` (Enclosure temperature)
- `turtle/sensors/sensor2/humidity` (Enclosure humidity)

## 🔧 Configuration

### Environment Variables
- `MQTT_BROKER=mosquitto` (Docker service name)
- `MQTT_PORT=1883`
- `DATABASE_PATH=/data/turtle_monitor.db`

### Status Ranges
- **Shell Temperature**: Normal 70-90°F, Warning 65-95°F
- **Enclosure Temperature**: Normal 70-85°F, Warning 65-90°F
- **Humidity**: Normal 60-80%, Warning 50-85%

## 🛠️ Management

### View Logs
```bash
# API logs
docker logs turtle-monitor-api

# MQTT logs
docker logs turtle-monitor-mqtt

# Deployment logs
cat /tmp/turtle-deploy.log
```

### Restart Services
```bash
# Restart API
docker restart turtle-monitor-api

# Restart MQTT
docker restart turtle-monitor-mqtt

# Restart all
docker-compose -f turtle-monitor/deployment/docker-compose.yml restart
```

### Update System
```bash
# Pull latest changes and redeploy
cd /home/turtle/turtx
git pull origin main
cd turtle-monitor/deployment
./deploy-turtle-api.sh
```

## 🔄 Migration Strategy

### Phase 1: Deploy API (Complete)
- ✅ API system deployed alongside existing services
- ✅ MQTT integration working
- ✅ Frontend accessible

### Phase 2: Test Kiosk Display (Next)
- Test the new interface manually
- Verify sensor data updates
- Check touchscreen responsiveness

### Phase 3: Switch Kiosk Service (Future)
- Update kiosk systemd service to point to new API
- Validate 24+ hours of stable operation
- Monitor for any issues

### Phase 4: Smart Plug Integration (Future)
- Integrate with Home Assistant API for smart plug control
- Add automation capabilities

## 🚨 Troubleshooting

### API Not Responding
```bash
# Check container status
docker ps | grep turtle-monitor

# Check API logs
docker logs turtle-monitor-api

# Test API directly
curl http://localhost:8000/api/health
```

### MQTT Issues
```bash
# Check MQTT broker
docker logs turtle-monitor-mqtt

# Test MQTT connectivity
mosquitto_pub -h localhost -t test -m "test"
```

### Frontend Issues
```bash
# Check frontend files
docker exec turtle-monitor-api ls -la /app/frontend

# Check API logs for frontend errors
docker logs turtle-monitor-api | grep -i frontend
```

### Rollback (If Needed)
```bash
# Stop new containers
docker-compose -f turtle-monitor/deployment/docker-compose.yml down

# Restart original kiosk service
sudo systemctl restart kiosk
```

## 📈 Performance Benefits

### Memory Usage
- **Previous WebSocket**: Memory leaks requiring frequent restarts
- **New HTTP API**: Stable memory usage, no leaks

### Reliability
- **Previous**: Connection drops, authentication issues
- **New**: Simple HTTP polling, automatic retry

### Maintenance
- **Previous**: Complex WebSocket debugging
- **New**: Standard HTTP/REST patterns

## 🎉 Success Criteria

The deployment is successful when:
- ✅ API responds to health checks
- ✅ Frontend loads and displays sensor data
- ✅ MQTT connectivity is stable
- ✅ No memory leaks over 2+ hours
- ✅ Touch interface is responsive
- ✅ Status indicators work correctly

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Test individual components
4. Consider rolling back if necessary

---

**🐢 The API-based kiosk system is ready to provide reliable, beautiful turtle monitoring! 🐢** 