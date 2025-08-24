# 🐢 Turtle Monitor Camera Integration

## Overview

The Turtle Monitor Camera Integration adds live video streaming capabilities to the existing turtle monitoring system using the Arducam 1080P Day & Night Vision USB Camera. This integration provides real-time habitat monitoring with automatic IR night vision detection, USB auto-recovery, and comprehensive health monitoring.

## Features

### 🎥 Camera Features
- **Live Video Stream**: MJPEG streaming optimized for web display
- **Auto IR Detection**: Automatic night vision mode switching based on ambient light
- **USB Auto-Recovery**: Automatic reconnection on USB disconnection events
- **Health Monitoring**: Comprehensive camera status with 60-second max recovery time
- **Snapshot Capture**: High-quality JPEG snapshots for notifications
- **Quality Adaptation**: Automatic resolution/framerate adjustment

### 🖥️ Dashboard Integration
- **Seamless Layout**: Camera feed integrated into existing turtle dashboard
- **Status Indicators**: Visual camera health and connection status
- **Responsive Design**: Scales properly on 1024×600 touchscreen
- **Error Handling**: Graceful camera offline mode with retry logic
- **Touch Optimization**: Camera controls suitable for touchscreen interface

### 🔧 System Features
- **Production Reliability**: Multi-layer recovery and health monitoring
- **Docker Integration**: Containerized deployment with proper device access
- **Nginx Proxy**: Optimized streaming with rate limiting and caching
- **Udev Rules**: Automatic device detection and service restart
- **Performance Optimized**: Minimal impact on existing sensor monitoring

## Hardware Requirements

### Camera Hardware
- **Device**: Arducam 1080P Day & Night Vision USB Camera
- **Resolution**: 1920×1080 (1080p) with auto-scaling for streaming
- **Features**: Auto IR switching, USB UVC compatible
- **Connection**: USB 2.0/3.0
- **Power**: USB powered

### System Requirements
- **USB Ports**: Available USB port for camera connection
- **Docker**: Docker and Docker Compose installed
- **Permissions**: Root access for udev rules installation
- **Network**: Local network access for streaming

## Installation

### 1. Prerequisites
```bash
# Ensure Docker is installed and running
sudo systemctl start docker
sudo usermod -a -G docker $USER

# Install required system packages
sudo apt update
sudo apt install -y v4l-utils curl jq
```

### 2. Camera Hardware Setup
```bash
# Connect the Arducam USB camera
# Check if camera is detected
ls -la /dev/video*

# Get camera information (if v4l2-ctl is available)
v4l2-ctl --list-devices
```

### 3. Deploy Camera Integration
```bash
# Navigate to project directory
cd turtle-monitor

# Run the camera deployment script (requires root for udev rules)
sudo ./deployment/deploy-camera.sh
```

### 4. Verify Installation
```bash
# Check service status
docker-compose ps

# Test camera endpoints
curl http://localhost:8000/api/camera/status
curl http://localhost:8000/api/camera/snapshot -o test-snapshot.jpg

# Access dashboard
open http://localhost:80
```

## API Endpoints

### Camera Status
```http
GET /api/camera/status
```
Returns comprehensive camera health and status information.

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "camera": {
    "connected": true,
    "device": "/dev/video0",
    "resolution": "1920x1080",
    "fps_target": 15,
    "fps_actual": 14.8,
    "ir_mode": false,
    "auto_ir": true,
    "quality": 85,
    "uptime": 3600.5,
    "frame_count": 54000,
    "error_count": 0,
    "last_error": null,
    "recovery_attempts": 0,
    "max_recovery_attempts": 5,
    "connection_status": "connected"
  },
  "status": "online"
}
```

### Camera Snapshot
```http
GET /api/camera/snapshot
```
Returns current camera frame as JPEG image.

### Camera Stream
```http
GET /api/camera/stream
```
Returns MJPEG video stream for live viewing.

### Camera Restart
```http
GET /api/camera/restart
```
Manually restart camera connection.

## Configuration

### Camera Settings
Camera settings are configured in `api/camera.py`:

```python
# Camera properties
self.frame_width = 1920
self.frame_height = 1080
self.fps = 15
self.quality = 85  # JPEG quality

# Camera settings for turtle monitoring
self.camera_settings = {
    'brightness': 50,
    'contrast': 50,
    'saturation': 50,
    'hue': 0,
    'gain': 50,
    'exposure': -6,  # Auto exposure
    'focus': 0,  # Auto focus
    'white_balance': 4600,  # Auto white balance
}
```

### Nginx Configuration
Streaming is optimized through Nginx configuration in `config/nginx.conf`:

- **Rate Limiting**: Camera endpoints have specific rate limits
- **Buffering**: Disabled for real-time streaming
- **Caching**: Optimized for snapshots and static content
- **CORS**: Configured for web access

### Udev Rules
Camera device access is managed through udev rules in `config/udev-camera.rules`:

- **Device Permissions**: Proper access for turtle group
- **Auto-Restart**: Service restart on USB events
- **Device Detection**: Support for multiple camera vendors

## Dashboard Features

### Camera Display
The camera feed is integrated into the main dashboard with:

- **Live Video**: Real-time MJPEG stream
- **Status Overlay**: Connection and IR mode indicators
- **Error Handling**: Graceful offline mode with retry
- **Responsive Design**: Scales for 1024×600 touchscreen

### Status Indicators
- **Connection Status**: Visual indicator for camera connectivity
- **IR Mode**: Purple indicator when night vision is active
- **Error States**: Clear indication of camera issues
- **Auto-Recovery**: Automatic retry with visual feedback

### Touch Interface
- **Touch-Friendly**: Large touch targets for camera controls
- **Gesture Support**: Hover effects and visual feedback
- **Error Recovery**: Easy camera restart through interface

## Troubleshooting

### Camera Not Detected
```bash
# Check USB devices
lsusb | grep -i camera

# Check video devices
ls -la /dev/video*

# Check udev rules
sudo udevadm info -a -n /dev/video0

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Camera Connection Issues
```bash
# Check camera service logs
docker-compose logs turtle-api

# Test camera API directly
curl -v http://localhost:8000/api/camera/status

# Restart camera service
curl http://localhost:8000/api/camera/restart

# Check camera device permissions
ls -la /dev/video0
```

### Streaming Issues
```bash
# Check Nginx logs
docker-compose logs nginx

# Test stream endpoint
curl -I http://localhost/api/camera/stream

# Check network connectivity
netstat -tlnp | grep :80
```

### Performance Issues
```bash
# Monitor system resources
docker stats

# Check camera FPS
curl -s http://localhost:8000/api/camera/status | jq '.camera.fps_actual'

# Adjust camera quality in api/camera.py
```

## Monitoring and Maintenance

### Health Monitoring
The camera system includes comprehensive health monitoring:

- **Connection Status**: Real-time camera connectivity
- **Frame Rate**: Actual vs target FPS monitoring
- **Error Tracking**: Error count and last error details
- **Recovery Attempts**: Automatic restart tracking
- **Uptime Monitoring**: Service uptime tracking

### Log Monitoring
```bash
# View real-time logs
docker-compose logs -f turtle-api

# Check camera-specific logs
docker-compose logs turtle-api | grep -i camera

# Monitor error rates
docker-compose logs turtle-api | grep -i error
```

### Performance Metrics
- **Stream Quality**: 1080p at 15-30 FPS depending on bandwidth
- **Recovery Time**: Maximum 60-second downtime for camera failures
- **Resource Usage**: Minimal CPU impact on sensor monitoring
- **Network Efficiency**: Optimized streaming via Nginx proxy

## Future Enhancements

### Motion Detection
The system includes a motion detection module (`camera/motion.py`) for future enhancement:

- **Zone Detection**: Turtle-specific activity zones
- **Motion Analysis**: Contour-based motion detection
- **Activity Tracking**: Historical motion statistics
- **Alert System**: Motion-based notifications

### Advanced Features
- **Recording**: Automatic video recording on motion
- **Time-lapse**: Daily habitat time-lapse videos
- **AI Detection**: Turtle behavior analysis
- **Mobile App**: Camera access via mobile application

## Security Considerations

### Network Security
- **Local Network Only**: Camera stream not exposed to internet
- **Rate Limiting**: API endpoints protected against abuse
- **Access Control**: Proper user/group permissions
- **HTTPS**: Consider SSL/TLS for production deployment

### Device Security
- **Device Permissions**: Proper camera device access control
- **Resource Limits**: Prevent camera service resource exhaustion
- **Error Handling**: Graceful failure without system impact
- **Logging**: Comprehensive audit trail for security events

## Support

### Getting Help
- **Logs**: Check Docker logs for detailed error information
- **API Testing**: Use curl commands to test endpoints
- **Hardware**: Verify camera connection and permissions
- **Documentation**: Refer to this guide for configuration details

### Common Issues
1. **Camera not detected**: Check USB connection and udev rules
2. **Stream not working**: Verify Nginx configuration and network
3. **Poor performance**: Adjust camera quality and FPS settings
4. **Permission errors**: Ensure proper device and group permissions

### Contact
For additional support or feature requests, please refer to the main project documentation or create an issue in the project repository. 