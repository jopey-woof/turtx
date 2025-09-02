# Turtle Monitoring System - Development Context

You are helping with a **turtle enclosure monitoring system** called **TurtX**. This is a real IoT project deployed on Ubuntu Server for monitoring turtle habitat conditions.

## Project Overview
- **Purpose**: Real-time monitoring of turtle habitat temperature and humidity
- **Hardware**: TEMPerHUM USB sensors in basking and cooling areas
- **Architecture**: MQTT → FastAPI → Nginx → Web Dashboard
- **Update Frequency**: 2-second real-time updates
- **Deployment**: Ubuntu Server at IP 10.0.20.69

## Current Architecture

```
TEMPerHUM Sensors → MQTT (Mosquitto) → FastAPI (Port 8001) → Nginx (Port 80) → Web Dashboard
```

## File Structure
```
/home/shrimp/turtx/
├── turtle-monitor/
│   ├── web/index.html              # Web dashboard (HTML/CSS/JS)
│   ├── api/main.py                 # FastAPI backend server
│   ├── api/requirements.txt        # Python dependencies
│   └── data/sensors.db             # SQLite database (auto-created)
├── hardware/
│   ├── temperhum_mqtt_service.py   # Sensor → MQTT publisher
│   └── temperhum_config.json       # Sensor configuration
└── deploy.sh                       # Deployment automation
```

## System Components

### 1. **Web Dashboard** (`/home/shrimp/turtx/turtle-monitor/web/index.html`)
- Modern, responsive HTML5 interface
- Real-time sensor data display (basking/cooling areas)
- Temperature history charts
- Alert system for out-of-range conditions
- Updates every 2 seconds via API calls

### 2. **FastAPI Backend** (`/home/shrimp/turtx/turtle-monitor/api/main.py`)
- Serves sensor data via REST API
- MQTT client for real-time sensor data
- SQLite database for data persistence
- Endpoints: `/health`, `/api/latest`, `/api/history/{zone}`, `/api/alerts`
- Background tasks for data management

### 3. **Nginx Configuration** (`/etc/nginx/sites-available/turtle-dashboard`)
- Reverse proxy to FastAPI (port 8001)
- Serves static web dashboard files
- Single URL access: http://10.0.20.69/
- CORS headers and security configuration

### 4. **MQTT Integration**
- Broker: Mosquitto on localhost:1883
- Topics: `turtle/sensors/{basking|cooling}/{temperature|humidity}`
- 2-second update frequency from TEMPerHUM sensors

## API Endpoints

```
GET  /health                    # System health check
GET  /api/latest               # Current sensor readings
GET  /api/history/{zone}       # Historical data (24h default)
GET  /api/alerts               # Current system alerts
GET  /api/stats                # System statistics
POST /api/test-data            # Inject demo data for testing
```

## Expected Data Format

```json
{
  "timestamp": "2024-08-23T15:30:00.000Z",
  "sensors": {
    "basking": {
      "temperature": 92.3,
      "humidity": 52.1,
      "timestamp": "2024-08-23T15:30:00.000Z",
      "fresh": true,
      "age_seconds": 1
    },
    "cooling": {
      "temperature": 78.5,
      "humidity": 68.9,
      "timestamp": "2024-08-23T15:30:00.000Z", 
      "fresh": true,
      "age_seconds": 1
    }
  }
}
```

## Temperature Ranges (Fahrenheit)
- **Basking Area**: 88-95°F (optimal), 40-60% humidity
- **Cooling Area**: 75-82°F (optimal), 60-80% humidity

## Current Issues Needing Resolution

1. **Nginx configuration problems** - may have conflicting server blocks or broken paths
2. **API architecture confusion** - endpoints may not be properly configured
3. **Missing or deleted work** - web dashboard or API files may be corrupted
4. **Dashboard not loading** - could be file permissions, nginx config, or API connectivity
5. **Cleanup needed** - Remove unused configuration attempts, broken files, and conflicting setups

## Development Guidelines

### When Writing Code:
- **Always check for existing files** before overwriting
- **Use proper error handling** for all API calls and file operations
- **Include logging** for debugging production issues
- **Follow the existing project structure** exactly
- **Test with demo data first**, then real sensors
- **Make it beautiful AND functional** - this is a showcase project

### Design Requirements:
- **Professional appearance** suitable for a kiosk display
- **Turtle/aquatic theming** with appropriate colors and icons
- **Responsive design** that works on different screen sizes
- **Real-time feel** with smooth updates and transitions
- **Clear status indicators** for system health

### Technical Requirements:
- **No external dependencies** except from cdnjs.cloudflare.com
- **Pure HTML/CSS/JS** for frontend (no build tools)
- **FastAPI with async/await** for backend
- **SQLite for persistence** (no complex databases)
- **Systemd service management** for production deployment

## Quick Commands for Development

```bash
# Check system status
sudo systemctl status turtle-api nginx mosquitto

# View logs
sudo journalctl -u turtle-api -f
sudo tail -f /var/log/nginx/turtle-dashboard-error.log

# Test API directly
curl http://localhost:8001/health
curl http://10.0.20.69/api/latest

# Inject test data
curl -X POST http://10.0.20.69/api/test-data

# Restart services
sudo systemctl restart turtle-api nginx

# Test nginx config
sudo nginx -t
```

## Current Deployment Status
- **System deployed** on Ubuntu Server 22.04 LTS
- **Base services running**: Mosquitto MQTT, basic file structure exists
- **Network**: Local access at 10.0.20.69
- **User context**: Running as 'shrimp' user
- **Production environment**: Real turtle habitat monitoring

## When I Ask for Help:
- **Focus on getting it working first**, then make it beautiful
- **Provide complete, working code** that I can deploy immediately
- **Include proper error handling** and logging for production use
- **Test your suggestions** with the actual file paths and structure
- **Consider the real-world turtle monitoring use case** in your solutions
- **Make it kiosk-ready** - this will be displayed 24/7 for turtle care

Remember: This is a **production system** for actual turtle care, so reliability and clear visual feedback are critical. The dashboard needs to work flawlessly and look professional enough for a dedicated monitoring kiosk.

## Project Phases (Complete Roadmap)

### Phase 1: Core Monitoring (CURRENT PRIORITY)
**Status**: In Progress - Dashboard needs fixing
- ✅ MQTT broker (Mosquitto) setup
- ✅ TEMPerHUM sensor integration with 2-second updates
- ✅ Basic FastAPI structure
- ❌ **Web dashboard not working** - needs immediate fix
- ❌ **Nginx configuration broken** - needs cleanup and repair
- ❌ **API connectivity issues** - needs debugging

### Phase 2: Camera Integration (NEXT)
**Status**: Ready to start once Phase 1 complete
- 📷 **Arducam 1080P USB camera** integration
- 🖼️ **Live video streaming** to dashboard
- 📸 **Snapshot capture** and storage
- 🎥 **Motion detection** for turtle activity monitoring
- 📱 **Mobile-friendly video** viewing

### Phase 3: Smart Automations (AFTER CAMERA)
**Status**: Planned
- 🌡️ **Temperature-based heating/cooling control**
- 💡 **Lighting automation** (basking lamps, UV lights)
- 💧 **Water circulation pump control**
- 🍽️ **Feeding schedule automation**
- 📊 **Smart alerts** via email/SMS for critical conditions
- 🧠 **ML-based behavior analysis** from camera data

### Phase 4: Advanced Features (FUTURE)
**Status**: Future development
- 🏠 **Home Assistant integration** complete
- 📈 **Long-term analytics** and health trending
- 📱 **Mobile app** for remote monitoring
- 🔐 **Multi-user access** with role-based permissions
- ☁️ **Cloud backup** and remote access (optional)
- 📋 **Maintenance scheduling** and reminders

### Phase 5: Production Polish (FINAL)
**Status**: Pre-deployment
- 🔒 **SSL/TLS encryption** for web access
- 🏗️ **System hardening** and security audit
- 📚 **Complete documentation** and user guides
- 🎛️ **Kiosk mode optimization** for dedicated display
- 🔄 **Automated backups** and disaster recovery
- 📊 **Performance monitoring** and optimization

## Hardware Integration Plan

### Current Hardware:
- **TEMPerHUM V4.1 USB sensors** (2x) - ✅ Working
- **Ubuntu Server 22.04** - ✅ Running
- **Network**: 10.0.20.69 on local network - ✅ Configured

### Phase 2 Hardware (Camera):
- **Arducam 1080P USB camera** - Ready to integrate
- **Additional USB hub** if needed for multiple devices

### Phase 3 Hardware (Automation):
- **Relay modules** for heating/cooling control
- **Smart switches** for lighting control
- **Water pump controllers**
- **Arduino/Raspberry Pi** for hardware interface (if needed)

### Phase 4 Hardware (Advanced):
- **UPS battery backup** for critical systems
- **Network storage** for video/data backup
- **Environmental sensors** (water quality, pH, etc.)

## Success Criteria for Each Phase

### Phase 1 Success (Web/Kiosk):
- [x] Dashboard loads instantly at http://10.0.20.69/
- [x] Real-time data updates every 2 seconds
- [x] Professional kiosk-ready appearance
- [x] Mobile responsive design
- [x] System health monitoring and alerts
- [x] Historical data charts and trends

### Phase 2 Success (Camera):
- [ ] Live video stream integrated into dashboard
- [ ] Automatic snapshot capture every hour
- [ ] Motion detection with turtle activity logging
- [ ] Video archive with easy playback
- [ ] Camera health monitoring

### Phase 3 Success (Automation):
- [ ] Automatic temperature control based on readings
- [ ] Lighting schedule automation (day/night cycle)
- [ ] Water circulation based on temperature/schedule
- [ ] Emergency alerts for critical conditions
- [ ] Manual override controls in dashboard

### Phase 4 Success (Advanced):
- [ ] Home Assistant full integration
- [ ] Mobile app for remote monitoring
- [ ] Cloud data backup and sync
- [ ] Advanced analytics and reporting
- [ ] Multi-device support

### Phase 5 Success (Production):
- [ ] SSL certificate installed and working
- [ ] Complete security audit passed
- [ ] Comprehensive documentation complete
- [ ] Automated backup system working
- [ ] 24/7 reliable operation demonstrated

## Immediate Action Items (Phase 1)

1. **Clean up broken configs** - Remove conflicting nginx sites, failed API attempts
2. **Fix nginx configuration** - Proper reverse proxy to FastAPI
3. **Repair/recreate dashboard** - Working HTML/CSS/JS with real-time updates
4. **Test API connectivity** - Ensure all endpoints working through nginx
5. **Verify MQTT data flow** - Sensors → MQTT → API → Dashboard
6. **Polish dashboard UI** - Make it kiosk-ready and professional
7. **Add comprehensive monitoring** - System health, alerts, error handling

Once Phase 1 is rock-solid, we immediately move to camera integration (Phase 2).