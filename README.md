# TurtX - Turtle Monitoring System 🐢

## 🚧 Status: ACTIVE DEVELOPMENT

The TurtX turtle monitoring system is currently **under active development** with a working prototype dashboard and kiosk interface.

## 🌟 Current Prototype

- **Dashboard**: http://10.0.20.69/
- **API**: http://10.0.20.69/api/latest
- **Home Assistant**: http://10.0.20.69:8123 (for automations)

## 🚀 Current Features

### Dashboard (In Development)
- **Real-time sensor data** - Temperature and humidity from both sensors
- **Multi-page navigation** - Status, Camera, and Data pages
- **Moon phase display** - Current lunar phase calculation
- **Live camera feed** - Integrated camera streaming (experimental)
- **Responsive design** - Optimized for 1024x600 touchscreen
- **Beautiful animations** - Star field and Nyan turtle animations
- **Theme system** - CSS custom properties for easy customization

### Infrastructure (Work in Progress)
- **FastAPI backend** - Serving sensor data and camera streams
- **Nginx proxy** - Configured with host networking
- **Docker containers** - API and nginx running with `network_mode: host`
- **Systemd kiosk service** - Chrome kiosk with auto-restart
- **Home Assistant integration** - Preserved for automation needs

## 📊 Development Status

### ✅ Working Components
- **Sensors**: Both sensor1 and sensor2 reporting data
- **Dashboard**: Functional TurtX interface (prototype)
- **API**: Real-time data flowing correctly
- **Kiosk**: Chrome instance displaying dashboard
- **Camera**: Basic streaming functional
- **Home Assistant**: Running for automations

### 🔧 Services
```bash
# Check system status
docker ps                    # API and nginx containers
systemctl --user status kiosk.service  # Kiosk service
ps aux | grep chrome        # Chrome processes
```

## 🏗️ Architecture (Current)

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
│   │   └── index.html              # Current dashboard prototype
│   ├── kiosk/
│   │   └── start-turtle-monitor-kiosk-simple.sh  # Kiosk script
│   └── turtle-monitor/
│       ├── deployment/
│       │   └── docker-compose.yml  # Docker services
│       ├── config/
│       │   └── nginx.conf          # Nginx configuration
│       └── api/                    # FastAPI backend
├── homeassistant/                  # Home Assistant configs
├── hardware/                       # Sensor configurations
├── daily-summaries/                # Development session logs
└── docs/                          # Documentation
```

## 🚀 Development Setup

To work with the current prototype:

```bash
# SSH to the development server
ssh shrimp@10.0.20.69

# Check services
docker ps
systemctl --user status kiosk.service

# View logs
docker logs turtle-monitor-api
journalctl --user -u kiosk.service
```

## 🔧 Current Configuration

### Kiosk Service
- **Location**: `/home/shrimp/.config/systemd/user/kiosk.service`
- **Script**: `start-turtle-monitor-kiosk-simple.sh`
- **URL**: `http://10.0.20.69/`

### Docker Services
- **API**: `turtle-monitor-api` (port 8000)
- **Nginx**: `turtle-monitor-nginx` (port 80)
- **Network**: Both using `network_mode: host`

## 📈 Current Monitoring

### Dashboard Features (Prototype)
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

## 🎯 Development Goals

- 🔄 **Improve dashboard stability**
- 🔄 **Enhance camera integration**
- 🔄 **Add more sensor types**
- 🔄 **Implement data logging**
- 🔄 **Add alerting system**
- 🔄 **Improve error handling**
- 🔄 **Add configuration UI**

## 📚 Documentation

- [Latest Session Summary](daily-summaries/2025/08/SESSION_COMPLETE.md) - Recent development progress
- [Hardware Setup](hardware/README.md) - Sensor configuration
- [Home Assistant Config](homeassistant/) - Automation setup

## 🤝 Contributing

This is an active development project. For contributions:

1. Check current development status
2. Test changes thoroughly
3. Update documentation
4. Ensure kiosk stability
5. Preserve Home Assistant functionality

## 🐛 Known Issues

- Camera streaming can be unstable
- Dashboard may need optimization for performance
- Error handling needs improvement
- Configuration management is basic

---

**TurtX is in active development! 🐢🚧**
