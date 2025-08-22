# TemperhUM USB Sensor Integration - Complete Solution

## 🐢 Turtle Enclosure Monitoring System

A complete, production-ready solution for integrating TemperhUM USB temperature and humidity sensors into a turtle enclosure monitoring system using Home Assistant.

## 🚀 Quick Start

### For End Users (One-Click Setup)

```bash
# On Ubuntu Server
cd /home/shrimp/turtle-monitor
./setup/install-temperhum.sh
```

### For Developers (Local Testing)

```bash
# Test the implementation locally
cd hardware
python3 test-temperhum-local.py
```

## 📋 What's Included

### Core Components

1. **`hardware/simple_data_capture.py`** - Main data capture script
   - Robust data parsing with error handling
   - Interval-based sensor identification (1S vs 2S)
   - MQTT auto-discovery for Home Assistant
   - Live debugging output
   - Systemd service integration

2. **`hardware/hid_controller.py`** - Linux HID control module
   - Device detection and management
   - Programmatic sensor control (research implementation)
   - udev rules setup
   - Permission handling

3. **`hardware/temperhum_manager.py`** - Full-featured manager
   - Complete sensor management system
   - Advanced HID control capabilities
   - Comprehensive error handling

### Setup & Deployment

4. **`setup/install-temperhum.sh`** - One-click installation script
   - Automatic dependency installation
   - udev rules configuration
   - MQTT broker setup
   - Systemd service installation
   - Comprehensive testing

5. **`setup/deploy-temperhum.sh`** - Remote deployment script
   - SSH-based deployment to Ubuntu server
   - File synchronization
   - Remote installation execution
   - Status verification

### Configuration Files

6. **`hardware/99-temperhum-sensors.rules`** - udev rules for device access
7. **`hardware/temperhum-capture.service`** - Systemd service configuration
8. **`hardware/requirements.txt`** - Python dependencies

### Testing & Documentation

9. **`hardware/test-temperhum-local.py`** - Comprehensive test suite
10. **`docs/TEMPERHUM-SETUP.md`** - Complete user documentation

## 🏗️ Architecture

### Sensor Strategy
- **Sensor 1**: 1-second intervals (`1S` suffix)
- **Sensor 2**: 2-second intervals (`2S` suffix)
- **Unified Data Stream**: Both sensors type into single file
- **Automatic Identification**: Parsed by interval suffix

### Data Flow
```
TemperhUM Sensors → /tmp/temperhum_data.txt → Python Parser → MQTT → Home Assistant
```

### MQTT Topics
- `turtle/sensors/temperhum/sensor_1/temperature`
- `turtle/sensors/temperhum/sensor_1/humidity`
- `turtle/sensors/temperhum/sensor_2/temperature`
- `turtle/sensors/temperhum/sensor_2/humidity`

## 🔧 Features

### ✅ Implemented
- ✅ Robust data parsing with validation
- ✅ Interval-based sensor identification
- ✅ MQTT auto-discovery for Home Assistant
- ✅ Systemd service for background operation
- ✅ Comprehensive error handling
- ✅ Live debugging output
- ✅ One-click installation
- ✅ Remote deployment
- ✅ Complete test suite
- ✅ Extensive documentation

### 🔬 Research Areas
- Linux HID programmatic control (complex, requires further development)
- Advanced sensor initialization
- Failsafe alerting mechanisms

## 📊 Data Format

### Expected Sensor Output
```
29.54[C]39.58[%RH]1S  ← Sensor 1 (1-second intervals)
27.60[C]40.38[%RH]2S  ← Sensor 2 (2-second intervals)
```

### Parsed Data Structure
```python
{
    "sensor_id": "sensor_1",
    "temperature": 29.54,
    "humidity": 39.58,
    "interval": 1,
    "timestamp": "2025-08-22T17:04:52.614405Z",
    "raw_line": "29.54[C]39.58[%RH]1S"
}
```

## 🛠️ Installation

### Prerequisites
- Ubuntu Server 24.04+
- Python 3.8+
- 2x TemperhUM V4.1 USB sensors
- Home Assistant (for monitoring)

### Automatic Installation
```bash
# Clone repository
git clone https://github.com/jopey-woof/turtx.git
cd turtx

# Run one-click setup
./setup/install-temperhum.sh
```

### Manual Installation
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev python3-evdev mosquitto

# Install Python packages
pip3 install --user paho-mqtt evdev python-evdev

# Setup udev rules
sudo cp hardware/99-temperhum-sensors.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules

# Install service
sudo cp hardware/temperhum-capture.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable temperhum-capture.service
sudo systemctl start temperhum-capture.service
```

## 🔍 Testing

### Local Test Suite
```bash
cd hardware
python3 test-temperhum-local.py
```

### Manual Testing
```bash
# Test data parsing
echo "29.54[C]39.58[%RH]1S" >> /tmp/temperhum_data.txt

# Check service status
sudo systemctl status temperhum-capture.service

# View logs
tail -f /var/log/temperhum-capture.log

# Monitor MQTT messages
mosquitto_sub -t "turtle/sensors/temperhum/#" -v
```

## 📖 Usage

### Sensor Configuration
1. Plug in both TemperhUM sensors
2. Configure Sensor 1 to 1-second intervals
3. Configure Sensor 2 to 2-second intervals
4. Activate sensors (hold Caps Lock for 1 second)

### Monitoring
```bash
# View live sensor data
tail -f /tmp/temperhum_data.txt

# Check service status
sudo systemctl status temperhum-capture.service

# View logs
tail -f /var/log/temperhum-capture.log
```

### Home Assistant Integration
Sensors are automatically discovered:
- `sensor.turtle_sensor_1_temperature`
- `sensor.turtle_sensor_1_humidity`
- `sensor.turtle_sensor_2_temperature`
- `sensor.turtle_sensor_2_humidity`

## 🐛 Troubleshooting

### Common Issues

**Sensors not detected:**
```bash
lsusb
ls /dev/input/
sudo udevadm test /sys/class/input/event*
```

**Permission errors:**
```bash
sudo usermod -a -G input $USER
ls -la /dev/input/
```

**Service not starting:**
```bash
sudo journalctl -u temperhum-capture.service -f
sudo systemctl status mosquitto
```

**No data appearing:**
```bash
tail -f /tmp/temperhum_data.txt
echo "29.54[C]39.58[%RH]1S" >> /tmp/temperhum_data.txt
```

### Debug Mode
```bash
sudo systemctl stop temperhum-capture.service
cd /home/shrimp/turtle-monitor/hardware
python3 simple_data_capture.py --debug
```

## 📚 Documentation

- **[Complete Setup Guide](docs/TEMPERHUM-SETUP.md)** - Detailed installation and usage instructions
- **[Hardware Documentation](hardware/)** - Technical implementation details
- **[Test Suite](hardware/test-temperhum-local.py)** - Comprehensive testing framework

## 🔒 Security

### Network Security
- MQTT broker configured for local access only
- Consider authentication for production use
- Firewall rules recommended

### Device Security
- udev rules grant broad input device access
- Consider more restrictive rules for production
- Regular system updates recommended

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite: `python3 test-temperhum-local.py`
5. Submit a pull request

## 📄 License

This project is part of the Turtle Monitoring System and follows the same licensing terms.

## 🆘 Support

### Getting Help
1. Check the [troubleshooting section](#-troubleshooting)
2. Review the [complete setup guide](docs/TEMPERHUM-SETUP.md)
3. Run the [test suite](hardware/test-temperhum-local.py)
4. Check service logs: `tail -f /var/log/temperhum-capture.log`

### Common Commands
| Command | Purpose |
|---------|---------|
| `sudo systemctl status temperhum-capture.service` | Check service status |
| `tail -f /var/log/temperhum-capture.log` | View live logs |
| `tail -f /tmp/temperhum_data.txt` | View sensor data |
| `mosquitto_sub -t "turtle/sensors/temperhum/#" -v` | Monitor MQTT messages |

---

**🐢 Built with care for turtle safety and monitoring** 🐢 