# TEMPerHUM USB Sensor Testing Solution

## 🎯 Overview

This solution provides a comprehensive, interactive testing system for TEMPerHUM USB temperature/humidity sensors on remote Linux machines. It's designed to help you quickly validate sensor functionality and troubleshoot issues in an attended, step-by-step process.

## 🚀 Quick Start

### Automated Testing (Recommended)

```bash
# Deploy and run the full interactive test
./setup/deploy-temperhum-test.sh
```

This single command will:
1. Copy the test script to your remote machine
2. Install all dependencies automatically
3. Run the interactive testing process
4. Save detailed results for review

### Quick Validation

```bash
# Run a quick test without full interaction
ssh shrimp@10.0.20.69 'cd /home/shrimp/turtle-monitor/hardware && python3 quick-temperhum-test.py'
```

## 📁 Files Created

### Core Testing Scripts
- **`hardware/temperhum_test_installer.py`** - Main interactive testing script
- **`hardware/quick-temperhum-test.py`** - Simplified validation script
- **`setup/deploy-temperhum-test.sh`** - Automated deployment script

### Documentation
- **`docs/TEMPERHUM-TESTING-GUIDE.md`** - Comprehensive testing guide
- **`README-TEMPERHUM-TESTING.md`** - This file

## 🔧 Features

### Interactive Testing Process
- **Step-by-step guidance** with clear prompts
- **Automatic dependency installation** (Python packages, system tools)
- **Device detection** (USB and HID enumeration)
- **Multiple testing methods** (programmatic and manual)
- **Comprehensive error handling** with troubleshooting suggestions

### Testing Methods
1. **Programmatic Reading** - Uses `temper-py` package for direct sensor communication
2. **Manual Activation** - Captures "typed" output from button-activated sensors
3. **Fallback Mechanisms** - Multiple approaches if primary method fails

### Data Formats Supported
- Standard TEMPerHUM: `32.73[C]36.82[%RH]1S`
- Temperature/Humidity: `32.73°C 36.82%`
- Descriptive: `Temp: 32.73°C, Humidity: 36.82%`

## 🎮 Usage Examples

### Full Interactive Test

```bash
# Deploy and run complete test
./setup/deploy-temperhum-test.sh
```

**Expected Output:**
```
============================================================
  TEMPerHUM USB Sensor Installer and Tester
============================================================

ℹ This script will guide you through installing and testing TEMPerHUM sensors
ℹ Make sure you have SSH access to the remote machine
ℹ Have your TEMPerHUM sensors ready

Press Enter to continue...

→ Checking Python version...
✓ Python 3.8.10 detected

→ Installing system dependencies...
ℹ Updating package list...
ℹ Installing python3-pip...
ℹ Installing python3-serial...
✓ Dependencies installed successfully

→ Detecting USB devices...
✓ TEMPerHUM sensor detected: Bus 001 Device 003: ID 413d:2107 TEMPerHUM

============================================================
  Testing Sensor 1
============================================================

Step 1: Verify sensor connection
Please ensure sensor 1 is plugged into a USB port, then press Enter...

Step 2: Detecting sensor...
✓ TEMPerHUM sensor detected: Bus 001 Device 003: ID 413d:2107 TEMPerHUM

Step 3: Attempting programmatic reading...
✓ temper-py output: 24.5°C 45.2%
✓ Programmatic reading successful!
```

### Quick Test

```bash
# SSH to remote and run quick test
ssh shrimp@10.0.20.69 'cd /home/shrimp/turtle-monitor/hardware && python3 quick-temperhum-test.py'
```

**Expected Output:**
```
TEMPerHUM Quick Test
===================
✓ Python version: 3.8.10

Checking dependencies...
✓ temper-py installed

Checking USB devices...
✓ TEMPerHUM detected: Bus 001 Device 003: ID 413d:2107 TEMPerHUM

Testing temper-py...
✓ temper.py working
  Output: 24.5°C 45.2%...

Quick manual test...
Press TXT button on sensor or hold Caps Lock for 3 seconds
Type the output you see (or 'skip' to skip):
Sensor output: 24.5°C 45.2%
✓ Manual test successful

==================================================
TEST SUMMARY
==================================================
Python: ✓ PASS
Dependencies: ✓ PASS
Usb Devices: ✓ PASS
Temper Py: ✓ PASS
Manual Test: ✓ PASS

Results: 5/5 tests passed

🎉 All tests passed! Sensors are working correctly.
```

## 🔍 Troubleshooting

### Common Issues

#### 1. No Sensors Detected
```bash
# Check USB devices
ssh shrimp@10.0.20.69 'lsusb | grep -i temperhum'

# Check system logs
ssh shrimp@10.0.20.69 'dmesg | tail -20'
```

**Solutions:**
- Ensure sensors are properly plugged in
- Check if sensor LED is illuminated
- Try different USB ports
- Verify sensor is not in special mode

#### 2. temper-py Installation Fails
```bash
# Manual installation
ssh shrimp@10.0.20.69 'pip3 install --user temper-py'

# Alternative installation
ssh shrimp@10.0.20.69 'python3 -m pip install temper-py'
```

#### 3. Permission Issues
```bash
# Add user to input group
ssh shrimp@10.0.20.69 'sudo usermod -a -G input shrimp'

# Check device permissions
ssh shrimp@10.0.20.69 'ls -la /dev/hidraw*'
```

#### 4. No Sensor Data
```bash
# Test manual activation
ssh shrimp@10.0.20.69 'python3 /tmp/temperhum_capture.py'

# Check sensor mode
# Press TXT button on sensor
# Hold Caps Lock for 3 seconds
```

### Debugging Commands

```bash
# Check service status
ssh shrimp@10.0.20.69 'sudo systemctl status temperhum-manager.service'

# View live logs
ssh shrimp@10.0.20.69 'sudo journalctl -u temperhum-manager.service -f'

# Monitor MQTT data
ssh shrimp@10.0.20.69 'mosquitto_sub -t "turtle/sensors/temperhum/#" -v'

# Check test results
ssh shrimp@10.0.20.69 'ls -la /tmp/temperhum_test_results_*.json'
```

## 📊 Test Results

### Results File Location
Test results are automatically saved to:
- `/tmp/temperhum_test_results_YYYYMMDD_HHMMSS.json`
- `/tmp/temperhum_quick_test_YYYYMMDD_HHMMSS.json`

### Results Format
```json
[
  {
    "sensor_id": 1,
    "method": "temper-py",
    "temperature": 24.5,
    "humidity": 45.2,
    "raw_output": "24.5°C 45.2%",
    "timestamp": "2025-01-20T14:30:22.123456"
  },
  {
    "sensor_id": 2,
    "method": "manual",
    "temperature": 24.3,
    "humidity": 44.8,
    "raw_data": "24.3[C]44.8[%RH]1S",
    "timestamp": "2025-01-20T14:31:15.654321"
  }
]
```

## 🔗 Integration

### With Home Assistant
After successful testing, integrate with Home Assistant:

```yaml
# homeassistant/sensors.yaml
- platform: mqtt
  name: "Turtle Enclosure Temperature"
  state_topic: "turtle/sensors/temperhum/sensor_1"
  value_template: "{{ value_json.temperature }}"
  unit_of_measurement: "°C"

- platform: mqtt
  name: "Turtle Enclosure Humidity"
  state_topic: "turtle/sensors/temperhum/sensor_1"
  value_template: "{{ value_json.humidity }}"
  unit_of_measurement: "%"
```

### With Existing System
The testing scripts are compatible with the existing turtle monitoring system:
- Uses same directory structure (`/home/shrimp/turtle-monitor/`)
- Compatible with existing udev rules
- Works with current systemd service configuration

## 📚 Documentation

### Detailed Guides
- **[TEMPerHUM Testing Guide](docs/TEMPERHUM-TESTING-GUIDE.md)** - Comprehensive testing instructions
- **[TEMPerHUM Implementation](docs/TEMPERHUM-IMPLEMENTATION.md)** - Full system implementation
- **[Hardware Setup](docs/HARDWARE.md)** - Hardware configuration details

### External Resources
- [TEMPerHUM Documentation](https://cdn.pcsensor.com/wp-content/uploads/2025/04/TEMPerHUM%E8%B6%85%E9%95%BF%E8%8B%B1%E6%96%87%E8%AF%B4%E6%98%8E%E4%B9%A6_EN_V6.pdf)
- [temper-py Package](https://pypi.org/project/temper-py/)
- [HID-TEMPerHUM GitHub](https://github.com/jeixav/HID-TEMPerHUM)

## 🎯 Success Criteria

A successful test should demonstrate:

✅ **Sensor Detection** - Both sensors identified via USB/HID  
✅ **Data Reading** - Temperature and humidity values retrieved  
✅ **Data Accuracy** - Readings within expected ranges (0-50°C, 0-100% RH)  
✅ **Reliability** - Consistent readings across multiple tests  
✅ **Integration Ready** - Data format compatible with Home Assistant  

## 🚀 Next Steps

After successful testing:

1. **Deploy Production System**
   ```bash
   ./setup/deploy-temperhum.sh
   ```

2. **Configure Home Assistant**
   - Add sensors to dashboard
   - Set up automations
   - Configure alerts

3. **Monitor Performance**
   - Check service logs
   - Monitor MQTT data flow
   - Validate sensor accuracy

## 🐢 Turtle Monitoring Context

This testing solution is part of the Eastern Box Turtle monitoring system, designed to:

- **Monitor Habitat Conditions** - Track temperature and humidity in turtle enclosures
- **Ensure Animal Welfare** - Maintain optimal environmental conditions
- **Automate Monitoring** - Reduce manual intervention requirements
- **Provide Alerts** - Notify when conditions are outside safe ranges

The system prioritizes reliability and ease of use, ensuring consistent monitoring of turtle habitat conditions.

---

**Built with care for our shelled friends** 🐢

This testing solution ensures reliable sensor operation for the eastern box turtle monitoring system, providing accurate environmental data for optimal habitat management. 