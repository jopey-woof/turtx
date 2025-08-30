# TurtX - Turtle Monitoring System 🐢

## 🎉 Status: PRODUCTION READY ✅

The TurtX turtle monitoring system is now **fully deployed and operational** with a beautiful, stable dashboard and kiosk interface.

## 🌟 Live System

- **Dashboard**: http://10.0.20.69/
- **API**: http://10.0.20.69/api/latest
- **Home Assistant**: http://10.0.20.69:8123 (for automations)

## 🚀 Features

### Dashboard
- **Real-time sensor data** - Temperature and humidity from both sensors
- **Multi-page navigation** - Status, Camera, and Data pages
- **Moon phase display** - Current lunar phase calculation
- **Live camera feed** - Integrated camera streaming
- **Responsive design** - Optimized for 1024x600 touchscreen
- **Beautiful animations** - Star field and Nyan turtle animations
- **Theme system** - CSS custom properties for easy customization

### Infrastructure
- **FastAPI backend** - Serving sensor data and camera streams
- **Nginx proxy** - Properly configured with host networking
- **Docker containers** - API and nginx running with `network_mode: host`
- **Systemd kiosk service** - Stable Chrome kiosk with auto-restart
- **Home Assistant integration** - Preserved for automation needs

## 📊 Current Status

### ✅ Working Components
- **Sensors**: Both sensor1 and sensor2 reporting data
- **Dashboard**: Beautiful, functional TurtX interface
- **API**: Real-time data flowing correctly
- **Kiosk**: Stable Chrome instance displaying dashboard
- **Camera**: Live streaming functional
- **Home Assistant**: Running for automations

### 🔧 Services
```bash
# Check system status
docker ps                    # API and nginx containers
systemctl --user status kiosk.service  # Kiosk service
ps aux | grep chrome        # Chrome processes
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Touchscreen   │    │   FastAPI       │    │   Home          │
│   Kiosk         │◄──►│   Backend       │◄──►│   Assistant     │
│   (Chrome)      │    │   (Docker)      │    │   (Automations) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   Nginx Proxy   │◄─────────────┘
                        │   (Docker)      │
                        └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │   Sensors       │
                        │   (MQTT)        │
                        └─────────────────┘
```

## 📁 Project Structure

```
turtx/
├── turtle-monitor/
│   ├── frontend/
│   │   └── index.html              # Production dashboard
│   ├── kiosk/
│   │   └── start-turtle-monitor-kiosk-simple.sh  # Stable kiosk script
│   └── turtle-monitor/
│       ├── deployment/
│       │   └── docker-compose.yml  # Docker services
│       ├── config/
│       │   └── nginx.conf          # Nginx configuration
│       └── api/                    # FastAPI backend
├── homeassistant/                  # Home Assistant configs
├── hardware/                       # Sensor configurations
└── docs/                          # Documentation
```

## 🚀 Quick Start

The system is already deployed and running. To check status:

```bash
# SSH to the server
ssh shrimp@10.0.20.69

# Check services
docker ps
systemctl --user status kiosk.service

# View logs
docker logs turtle-monitor-api
journalctl --user -u kiosk.service
```

## 🔧 Configuration

### Kiosk Service
- **Location**: `/home/shrimp/.config/systemd/user/kiosk.service`
- **Script**: `start-turtle-monitor-kiosk-simple.sh`
- **URL**: `http://10.0.20.69/`

### Docker Services
- **API**: `turtle-monitor-api` (port 8000)
- **Nginx**: `turtle-monitor-nginx` (port 80)
- **Network**: Both using `network_mode: host`

## 📈 Monitoring

### Dashboard Features
- Real-time temperature and humidity display
- Sensor connection status
- Data freshness indicators
- Error count tracking
- Connection alerts

### API Endpoints
- `GET /` - Dashboard interface
- `GET /api/latest` - Sensor data
- `GET /api/health` - System health
- `GET /api/camera/stream` - Camera feed

## 🎯 Success Metrics

- ✅ **Single, production-ready dashboard**
- ✅ **Real-time sensor data display**
- ✅ **Stable kiosk configuration**
- ✅ **No crashes or reloads**
- ✅ **Beautiful, functional UI**
- ✅ **Proper API integration**
- ✅ **Home Assistant preserved**

## 📚 Documentation

- [Session Complete Summary](SESSION_COMPLETE.md) - Detailed deployment summary
- [Hardware Setup](hardware/README.md) - Sensor configuration
- [Home Assistant Config](homeassistant/) - Automation setup

## 🤝 Contributing

The system is now in production. For enhancements or issues:

1. Test changes thoroughly
2. Update documentation
3. Ensure kiosk stability
4. Preserve Home Assistant functionality

---

**TurtX is live and monitoring! 🐢✨**
