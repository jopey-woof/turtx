#!/bin/bash

# Turtle Kiosk Dashboard - One-Command Setup
# This script creates a standalone turtle dashboard that connects directly to MQTT

set -e

echo "🐢 Turtle Kiosk Dashboard Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Set Home Assistant IP (known for this deployment)
HA_IP="10.0.20.69"
print_status "Using Home Assistant IP: $HA_IP"

# Create project directory
PROJECT_DIR="/home/$USER/turtle-dashboard"
print_info "Creating project directory: $PROJECT_DIR"

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Install dependencies
print_info "Installing system dependencies..."
echo "shrimp" | sudo -S apt update
echo "shrimp" | sudo -S apt install -y nginx python3 python3-pip mosquitto-clients chromium-browser

# Create web server configuration
print_info "Configuring web server..."

sudo tee /etc/nginx/sites-available/turtle-dashboard > /dev/null <<EOF
server {
    listen 8080;
    server_name localhost;
    root $PROJECT_DIR;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ =404;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Cache static files
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Disable default nginx site
server {
    listen 80 default_server;
    server_name _;
    return 444;
}
EOF

# Enable turtle dashboard site
echo "shrimp" | sudo -S ln -sf /etc/nginx/sites-available/turtle-dashboard /etc/nginx/sites-enabled/
echo "shrimp" | sudo -S rm -f /etc/nginx/sites-enabled/default

# Create dashboard files
print_info "Creating dashboard files..."

# Create index.html with MQTT host parameter
cat > index.html <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐢 Turtle Habitat Monitor</title>
    <link rel="stylesheet" href="css/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <h1 class="title">🐢 Turtle Habitat Monitor</h1>
                <div class="connection-status" id="connectionStatus">
                    <span class="status-dot" id="statusDot"></span>
                    <span class="status-text" id="statusText">Connecting...</span>
                </div>
            </div>
        </header>

        <!-- Main Dashboard -->
        <main class="dashboard">
            <!-- Sensor Cards -->
            <div class="sensor-grid">
                <!-- Sensor 1 -->
                <div class="sensor-card" id="sensor1">
                    <div class="sensor-header">
                        <h3>🌡️ Sensor 1</h3>
                        <div class="sensor-location">Main Habitat</div>
                    </div>
                    <div class="sensor-data">
                        <div class="data-row">
                            <div class="data-item">
                                <div class="data-label">Temperature</div>
                                <div class="data-value" id="temp1">--</div>
                                <div class="data-unit">°C</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Humidity</div>
                                <div class="data-value" id="hum1">--</div>
                                <div class="data-unit">%</div>
                            </div>
                        </div>
                        <div class="last-update" id="update1">Last update: Never</div>
                    </div>
                </div>

                <!-- Sensor 2 -->
                <div class="sensor-card" id="sensor2">
                    <div class="sensor-header">
                        <h3>🌡️ Sensor 2</h3>
                        <div class="sensor-location">Basking Area</div>
                    </div>
                    <div class="sensor-data">
                        <div class="data-row">
                            <div class="data-item">
                                <div class="data-label">Temperature</div>
                                <div class="data-value" id="temp2">--</div>
                                <div class="data-unit">°C</div>
                            </div>
                            <div class="data-item">
                                <div class="data-label">Humidity</div>
                                <div class="data-value" id="hum2">--</div>
                                <div class="data-unit">%</div>
                            </div>
                        </div>
                        <div class="last-update" id="update2">Last update: Never</div>
                    </div>
                </div>
            </div>

            <!-- Status Overview -->
            <div class="status-overview">
                <div class="status-card">
                    <h3>📊 Habitat Status</h3>
                    <div class="status-grid">
                        <div class="status-item" id="tempStatus">
                            <div class="status-icon">🌡️</div>
                            <div class="status-info">
                                <div class="status-label">Temperature</div>
                                <div class="status-value" id="tempStatusValue">Optimal</div>
                            </div>
                        </div>
                        <div class="status-item" id="humStatus">
                            <div class="status-icon">💧</div>
                            <div class="status-info">
                                <div class="status-label">Humidity</div>
                                <div class="status-value" id="humStatusValue">Optimal</div>
                            </div>
                        </div>
                        <div class="status-item" id="overallStatus">
                            <div class="status-icon">🐢</div>
                            <div class="status-info">
                                <div class="status-label">Overall</div>
                                <div class="status-value" id="overallStatusValue">Excellent</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Stats -->
            <div class="quick-stats">
                <div class="stat-card">
                    <div class="stat-icon">📈</div>
                    <div class="stat-content">
                        <div class="stat-value" id="avgTemp">--</div>
                        <div class="stat-label">Avg Temp (°C)</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">💧</div>
                    <div class="stat-content">
                        <div class="stat-value" id="avgHum">--</div>
                        <div class="stat-label">Avg Humidity (%)</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⏰</div>
                    <div class="stat-content">
                        <div class="stat-value" id="uptime">--</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="footer">
            <div class="footer-content">
                <div class="timestamp" id="currentTime">Loading...</div>
                <div class="version">Turtle Monitor v1.0</div>
            </div>
        </footer>
    </div>

    <!-- Loading Overlay -->
    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-text">Connecting to sensors...</div>
        </div>
    </div>

    <script src="js/app.js"></script>
</body>
</html>
EOF

# Create CSS directory and file
mkdir -p css
cat > css/style.css <<'EOF'
/* Turtle Habitat Monitor - Beautiful Earth-Toned Theme */

:root {
    --primary-green: #2d5a27;
    --secondary-green: #4a7c59;
    --accent-green: #6b8e23;
    --warm-brown: #8b4513;
    --light-brown: #d2b48c;
    --cream: #f5f5dc;
    --dark-earth: #3e2723;
    --success-green: #4caf50;
    --warning-orange: #ff9800;
    --danger-red: #f44336;
    --info-blue: #2196f3;
    
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-size-small: 0.875rem;
    --font-size-normal: 1rem;
    --font-size-large: 1.25rem;
    --font-size-xl: 1.5rem;
    --font-size-2xl: 2rem;
    
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    
    --border-radius-sm: 8px;
    --border-radius-md: 12px;
    --border-radius-lg: 16px;
    --border-radius-xl: 24px;
    
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.15);
    --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-family);
    background: linear-gradient(135deg, var(--primary-green) 0%, var(--secondary-green) 100%);
    color: var(--cream);
    min-height: 100vh;
    overflow-x: hidden;
    touch-action: manipulation;
}

.container {
    max-width: 1024px;
    margin: 0 auto;
    padding: var(--spacing-md);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: var(--shadow-md);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--spacing-md);
}

.title {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    color: var(--cream);
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.connection-status {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    background: rgba(0, 0, 0, 0.2);
    border-radius: var(--border-radius-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.status-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--warning-orange);
    animation: pulse 2s infinite;
}

.status-dot.connected {
    background: var(--success-green);
    animation: none;
}

.status-dot.disconnected {
    background: var(--danger-red);
    animation: none;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.status-text {
    font-size: var(--font-size-small);
    font-weight: 500;
}

.dashboard {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.sensor-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
}

.sensor-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.sensor-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--accent-green), var(--secondary-green));
    border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
}

.sensor-header {
    margin-bottom: var(--spacing-lg);
    text-align: center;
}

.sensor-header h3 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    margin-bottom: var(--spacing-xs);
    color: var(--cream);
}

.sensor-location {
    font-size: var(--font-size-small);
    color: rgba(255, 255, 255, 0.7);
    font-weight: 400;
}

.sensor-data {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
}

.data-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
}

.data-item {
    text-align: center;
    padding: var(--spacing-md);
    background: rgba(0, 0, 0, 0.2);
    border-radius: var(--border-radius-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.data-label {
    font-size: var(--font-size-small);
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: var(--spacing-xs);
    font-weight: 500;
}

.data-value {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    color: var(--cream);
    margin-bottom: var(--spacing-xs);
}

.data-unit {
    font-size: var(--font-size-small);
    color: rgba(255, 255, 255, 0.6);
    font-weight: 400;
}

.last-update {
    font-size: var(--font-size-small);
    color: rgba(255, 255, 255, 0.6);
    text-align: center;
    font-style: italic;
}

.status-overview {
    margin-bottom: var(--spacing-lg);
}

.status-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: var(--shadow-md);
}

.status-card h3 {
    font-size: var(--font-size-xl);
    font-weight: 600;
    margin-bottom: var(--spacing-lg);
    color: var(--cream);
    text-align: center;
}

.status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
}

.status-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: rgba(0, 0, 0, 0.2);
    border-radius: var(--border-radius-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
}

.status-icon {
    font-size: var(--font-size-xl);
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius-md);
}

.status-info {
    flex: 1;
}

.status-label {
    font-size: var(--font-size-small);
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: var(--spacing-xs);
    font-weight: 500;
}

.status-value {
    font-size: var(--font-size-normal);
    font-weight: 600;
    color: var(--cream);
}

.status-item.optimal .status-value {
    color: var(--success-green);
}

.status-item.warning .status-value {
    color: var(--warning-orange);
}

.status-item.danger .status-value {
    color: var(--danger-red);
}

.quick-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: var(--spacing-md);
}

.stat-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-lg);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    transition: all 0.3s ease;
}

.stat-icon {
    font-size: var(--font-size-xl);
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.1);
    border-radius: var(--border-radius-md);
}

.stat-content {
    flex: 1;
}

.stat-value {
    font-size: var(--font-size-large);
    font-weight: 700;
    color: var(--cream);
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    font-size: var(--font-size-small);
    color: rgba(255, 255, 255, 0.7);
    font-weight: 400;
}

.footer {
    margin-top: auto;
    padding-top: var(--spacing-lg);
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-md);
    background: rgba(0, 0, 0, 0.2);
    border-radius: var(--border-radius-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: var(--font-size-small);
    color: rgba(255, 255, 255, 0.7);
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(45, 90, 39, 0.95);
    backdrop-filter: blur(10px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    transition: opacity 0.3s ease;
}

.loading-overlay.hidden {
    opacity: 0;
    pointer-events: none;
}

.loading-content {
    text-align: center;
    color: var(--cream);
}

.loading-spinner {
    width: 60px;
    height: 60px;
    border: 4px solid rgba(255, 255, 255, 0.2);
    border-top: 4px solid var(--accent-green);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto var(--spacing-lg);
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-text {
    font-size: var(--font-size-large);
    font-weight: 500;
}

@media (max-width: 768px) {
    .container {
        padding: var(--spacing-sm);
    }
    
    .header-content {
        flex-direction: column;
        text-align: center;
    }
    
    .title {
        font-size: var(--font-size-xl);
    }
    
    .sensor-grid {
        grid-template-columns: 1fr;
    }
    
    .data-row {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
    }
    
    .status-grid {
        grid-template-columns: 1fr;
    }
    
    .quick-stats {
        grid-template-columns: 1fr;
    }
    
    .footer-content {
        flex-direction: column;
        gap: var(--spacing-sm);
        text-align: center;
    }
}
EOF

# Create JavaScript directory and file
mkdir -p js
cat > js/app.js <<EOF
/**
 * Turtle Habitat Monitor - MQTT Dashboard Application
 */

class TurtleDashboard {
    constructor() {
        this.client = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 5000;
        
        this.sensorData = {
            sensor1: { temperature: null, humidity: null, lastUpdate: null },
            sensor2: { temperature: null, humidity: null, lastUpdate: null }
        };
        
        this.config = {
            mqttBroker: 'ws://$HA_IP:9001',
            clientId: 'turtle-kiosk-' + Math.random().toString(16).substr(2, 8),
            topics: {
                sensor1Temp: 'turtle/sensor1/temperature',
                sensor1Hum: 'turtle/sensor1/humidity',
                sensor2Temp: 'turtle/sensor2/temperature',
                sensor2Hum: 'turtle/sensor2/humidity'
            }
        };
        
        this.init();
    }
    
    async init() {
        console.log('🐢 Initializing Turtle Dashboard...');
        this.initUI();
        this.connectMQTT();
        this.startUIUpdates();
    }
    
    initUI() {
        this.updateConnectionStatus('connecting');
        this.updateTime();
        this.startTime = Date.now();
        this.updateUptime();
    }
    
    connectMQTT() {
        console.log('🔌 Connecting to MQTT broker:', this.config.mqttBroker);
        
        try {
            this.client = mqtt.connect(this.config.mqttBroker, {
                clientId: this.config.clientId,
                clean: true,
                reconnectPeriod: 5000,
                connectTimeout: 30000,
                rejectUnauthorized: false
            });
            
            this.client.on('connect', () => {
                console.log('✅ Connected to MQTT broker');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
                this.subscribeToTopics();
                this.hideLoadingOverlay();
            });
            
            this.client.on('message', (topic, message) => {
                this.handleMessage(topic, message.toString());
            });
            
            this.client.on('error', (error) => {
                console.error('❌ MQTT Error:', error);
                this.updateConnectionStatus('error');
            });
            
            this.client.on('close', () => {
                console.log('🔌 MQTT connection closed');
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                this.showLoadingOverlay();
            });
            
            this.client.on('reconnect', () => {
                console.log('🔄 Reconnecting to MQTT...');
                this.updateConnectionStatus('reconnecting');
            });
            
        } catch (error) {
            console.error('❌ Failed to create MQTT client:', error);
            this.updateConnectionStatus('error');
            this.scheduleReconnect();
        }
    }
    
    subscribeToTopics() {
        if (!this.client || !this.isConnected) return;
        
        const topics = Object.values(this.config.topics);
        console.log('📡 Subscribing to topics:', topics);
        
        topics.forEach(topic => {
            this.client.subscribe(topic, (err) => {
                if (err) {
                    console.error(\`❌ Failed to subscribe to \${topic}:\`, err);
                } else {
                    console.log(\`✅ Subscribed to \${topic}\`);
                }
            });
        });
    }
    
    handleMessage(topic, message) {
        console.log(\`📨 Received message on \${topic}:\`, message);
        
        try {
            const value = parseFloat(message);
            if (isNaN(value)) {
                console.warn(\`⚠️ Invalid numeric value on \${topic}:\`, message);
                return;
            }
            
            if (topic === this.config.topics.sensor1Temp) {
                this.sensorData.sensor1.temperature = value;
                this.sensorData.sensor1.lastUpdate = new Date();
                this.updateSensorDisplay('sensor1', 'temperature', value);
            } else if (topic === this.config.topics.sensor1Hum) {
                this.sensorData.sensor1.humidity = value;
                this.sensorData.sensor1.lastUpdate = new Date();
                this.updateSensorDisplay('sensor1', 'humidity', value);
            } else if (topic === this.config.topics.sensor2Temp) {
                this.sensorData.sensor2.temperature = value;
                this.sensorData.sensor2.lastUpdate = new Date();
                this.updateSensorDisplay('sensor2', 'temperature', value);
            } else if (topic === this.config.topics.sensor2Hum) {
                this.sensorData.sensor2.humidity = value;
                this.sensorData.sensor2.lastUpdate = new Date();
                this.updateSensorDisplay('sensor2', 'humidity', value);
            }
            
            this.updateStatus();
            this.updateAverages();
            
        } catch (error) {
            console.error('❌ Error processing message:', error);
        }
    }
    
    updateSensorDisplay(sensorId, type, value) {
        const elementId = type === 'temperature' ? \`temp\${sensorId.slice(-1)}\` : \`hum\${sensorId.slice(-1)}\`;
        const element = document.getElementById(elementId);
        
        if (element) {
            element.textContent = value.toFixed(1);
            element.style.transform = 'scale(1.1)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
        
        const updateElement = document.getElementById(\`update\${sensorId.slice(-1)}\`);
        if (updateElement) {
            updateElement.textContent = \`Last update: \${new Date().toLocaleTimeString()}\`;
        }
    }
    
    updateStatus() {
        const temps = [this.sensorData.sensor1.temperature, this.sensorData.sensor2.temperature].filter(t => t !== null);
        const hums = [this.sensorData.sensor1.humidity, this.sensorData.sensor2.humidity].filter(h => h !== null);
        
        const avgTemp = temps.length > 0 ? temps.reduce((a, b) => a + b) / temps.length : null;
        const avgHum = hums.length > 0 ? hums.reduce((a, b) => a + b) / hums.length : null;
        
        this.updateStatusItem('tempStatus', avgTemp, {
            optimal: { min: 20, max: 30, color: 'optimal', text: 'Optimal' },
            warning: { min: 15, max: 35, color: 'warning', text: 'Attention' },
            danger: { min: -Infinity, max: Infinity, color: 'danger', text: 'Critical' }
        });
        
        this.updateStatusItem('humStatus', avgHum, {
            optimal: { min: 60, max: 80, color: 'optimal', text: 'Optimal' },
            warning: { min: 50, max: 90, color: 'warning', text: 'Attention' },
            danger: { min: -Infinity, max: Infinity, color: 'danger', text: 'Critical' }
        });
        
        this.updateOverallStatus();
    }
    
    updateStatusItem(elementId, value, thresholds) {
        const element = document.getElementById(elementId);
        const valueElement = document.getElementById(elementId + 'Value');
        
        if (!element || !valueElement || value === null) return;
        
        let status = 'optimal';
        let text = 'Optimal';
        
        if (value < thresholds.optimal.min || value > thresholds.optimal.max) {
            if (value < thresholds.warning.min || value > thresholds.warning.max) {
                status = 'danger';
                text = 'Critical';
            } else {
                status = 'warning';
                text = 'Attention';
            }
        }
        
        element.className = \`status-item \${status}\`;
        valueElement.textContent = text;
    }
    
    updateOverallStatus() {
        const tempStatus = document.getElementById('tempStatusValue')?.textContent;
        const humStatus = document.getElementById('humStatusValue')?.textContent;
        const overallElement = document.getElementById('overallStatus');
        const overallValueElement = document.getElementById('overallStatusValue');
        
        if (!overallElement || !overallValueElement) return;
        
        let overallStatus = 'optimal';
        let overallText = 'Excellent';
        
        if (tempStatus === 'Critical' || humStatus === 'Critical') {
            overallStatus = 'danger';
            overallText = 'Critical';
        } else if (tempStatus === 'Attention' || humStatus === 'Attention') {
            overallStatus = 'warning';
            overallText = 'Needs Attention';
        }
        
        overallElement.className = \`status-item \${overallStatus}\`;
        overallValueElement.textContent = overallText;
    }
    
    updateAverages() {
        const temps = [this.sensorData.sensor1.temperature, this.sensorData.sensor2.temperature].filter(t => t !== null);
        const hums = [this.sensorData.sensor1.humidity, this.sensorData.sensor2.humidity].filter(h => h !== null);
        
        const avgTemp = temps.length > 0 ? temps.reduce((a, b) => a + b) / temps.length : null;
        const avgHum = hums.length > 0 ? hums.reduce((a, b) => a + b) / hums.length : null;
        
        const avgTempElement = document.getElementById('avgTemp');
        const avgHumElement = document.getElementById('avgHum');
        
        if (avgTempElement) {
            avgTempElement.textContent = avgTemp !== null ? avgTemp.toFixed(1) : '--';
        }
        
        if (avgHumElement) {
            avgHumElement.textContent = avgHum !== null ? avgHum.toFixed(1) : '--';
        }
    }
    
    updateConnectionStatus(status) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (!statusDot || !statusText) return;
        
        switch (status) {
            case 'connected':
                statusDot.className = 'status-dot connected';
                statusText.textContent = 'Connected';
                break;
            case 'connecting':
                statusDot.className = 'status-dot';
                statusText.textContent = 'Connecting...';
                break;
            case 'reconnecting':
                statusDot.className = 'status-dot';
                statusText.textContent = 'Reconnecting...';
                break;
            case 'disconnected':
                statusDot.className = 'status-dot disconnected';
                statusText.textContent = 'Disconnected';
                break;
            case 'error':
                statusDot.className = 'status-dot disconnected';
                statusText.textContent = 'Connection Error';
                break;
        }
    }
    
    updateTime() {
        const timeElement = document.getElementById('currentTime');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleString();
        }
    }
    
    updateUptime() {
        const uptimeElement = document.getElementById('uptime');
        if (uptimeElement && this.startTime) {
            const uptime = Date.now() - this.startTime;
            const hours = Math.floor(uptime / (1000 * 60 * 60));
            const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
            uptimeElement.textContent = \`\${hours}h \${minutes}m\`;
        }
    }
    
    showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(\`🔄 Scheduling reconnect attempt \${this.reconnectAttempts}/\${this.maxReconnectAttempts} in \${this.reconnectDelay}ms\`);
            
            setTimeout(() => {
                this.connectMQTT();
            }, this.reconnectDelay);
        } else {
            console.error('❌ Max reconnect attempts reached');
            this.updateConnectionStatus('error');
        }
    }
    
    startUIUpdates() {
        setInterval(() => {
            this.updateTime();
        }, 1000);
        
        setInterval(() => {
            this.updateUptime();
        }, 60000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting Turtle Dashboard...');
    window.turtleDashboard = new TurtleDashboard();
});

document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log('📱 Page became visible, refreshing connection...');
        if (window.turtleDashboard && !window.turtleDashboard.isConnected) {
            window.turtleDashboard.connectMQTT();
        }
    }
});

window.addEventListener('beforeunload', () => {
    if (window.turtleDashboard && window.turtleDashboard.client) {
        window.turtleDashboard.client.end();
    }
});
EOF

# Set proper permissions
chmod 644 index.html
chmod 644 css/style.css
chmod 644 js/app.js

# Create systemd services
print_info "Creating systemd services..."

# Turtle Dashboard Web Server Service
sudo tee /etc/systemd/system/turtle-dashboard.service > /dev/null <<EOF
[Unit]
Description=Turtle Dashboard Web Server
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/sbin/nginx -g "daemon off;"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Turtle Kiosk Browser Service
sudo tee /etc/systemd/system/turtle-kiosk.service > /dev/null <<EOF
[Unit]
Description=Turtle Kiosk Browser
After=graphical-session.target turtle-dashboard.service
Wants=graphical-session.target

[Service]
Type=simple
User=$USER
Group=$USER
Environment=DISPLAY=:0
ExecStart=/usr/bin/chromium-browser --kiosk --disable-web-security --disable-features=VizDisplayCompositor --no-first-run --no-default-browser-check --disable-background-timer-throttling --disable-renderer-backgrounding --disable-backgrounding-occluded-windows --disable-ipc-flooding-protection --disable-background-networking --disable-default-apps --disable-extensions --disable-sync --disable-translate --hide-scrollbars --mute-audio --no-sandbox --disable-dev-shm-usage http://localhost:8080
Restart=always
RestartSec=10

[Install]
WantedBy=graphical-session.target
EOF

# Enable and start services
print_info "Enabling and starting services..."

echo "shrimp" | sudo -S systemctl daemon-reload
echo "shrimp" | sudo -S systemctl enable turtle-dashboard.service
echo "shrimp" | sudo -S systemctl enable turtle-kiosk.service

echo "shrimp" | sudo -S systemctl start turtle-dashboard.service
print_status "Web server started on port 8080"

# Test web server
sleep 2
if curl -s http://localhost:8080 > /dev/null; then
    print_status "Web server is responding correctly"
else
    print_warning "Web server may not be responding yet"
fi

# Create startup script
cat > start-turtle-kiosk.sh <<EOF
#!/bin/bash
# Start Turtle Kiosk Dashboard

echo "🐢 Starting Turtle Kiosk Dashboard..."

# Start web server if not running
if ! systemctl is-active --quiet turtle-dashboard.service; then
    echo "Starting web server..."
    sudo systemctl start turtle-dashboard.service
    sleep 2
fi

# Start kiosk browser
echo "Starting kiosk browser..."
sudo systemctl start turtle-kiosk.service

echo "✅ Turtle Kiosk Dashboard is running!"
echo "🌐 Dashboard URL: http://localhost:8080"
echo "🖥️  Kiosk mode: Active"
EOF

chmod +x start-turtle-kiosk.sh

# Create stop script
cat > stop-turtle-kiosk.sh <<EOF
#!/bin/bash
# Stop Turtle Kiosk Dashboard

echo "🛑 Stopping Turtle Kiosk Dashboard..."

sudo systemctl stop turtle-kiosk.service
sudo systemctl stop turtle-dashboard.service

echo "✅ Turtle Kiosk Dashboard stopped"
EOF

chmod +x stop-turtle-kiosk.sh

# Create status script
cat > status-turtle-kiosk.sh <<EOF
#!/bin/bash
# Check Turtle Kiosk Dashboard Status

echo "🐢 Turtle Kiosk Dashboard Status"
echo "================================"

echo "Web Server:"
systemctl is-active --quiet turtle-dashboard.service && echo "✅ Running" || echo "❌ Stopped"

echo "Kiosk Browser:"
systemctl is-active --quiet turtle-kiosk.service && echo "✅ Running" || echo "❌ Stopped"

echo ""
echo "Dashboard URL: http://localhost:8080"
echo "MQTT Broker: $HA_IP:9001"
EOF

chmod +x status-turtle-kiosk.sh

# Create README
cat > README.md <<EOF
# Turtle Kiosk Dashboard

A standalone turtle habitat monitoring dashboard that connects directly to MQTT.

## Features

- 🌡️ Real-time temperature and humidity monitoring
- 📊 Beautiful turtle-themed interface
- 🔌 Direct MQTT connection (no Home Assistant login required)
- 🖥️ Kiosk mode for touchscreen displays
- 🔄 Auto-restart on connection loss
- 📱 Responsive design for 1024x600 screens

## Quick Start

1. **Start the dashboard:**
   \`\`\`bash
   ./start-turtle-kiosk.sh
   \`\`\`

2. **Stop the dashboard:**
   \`\`\`bash
   ./stop-turtle-kiosk.sh
   \`\`\`

3. **Check status:**
   \`\`\`bash
   ./status-turtle-kiosk.sh
   \`\`\`

## Configuration

- **MQTT Broker:** $HA_IP:9001
- **Web Server:** http://localhost:8080
- **Topics:**
  - turtle/sensor1/temperature
  - turtle/sensor1/humidity
  - turtle/sensor2/temperature
  - turtle/sensor2/humidity

## Auto-Start

The dashboard will automatically start on boot. To disable:

\`\`\`bash
sudo systemctl disable turtle-dashboard.service
sudo systemctl disable turtle-kiosk.service
\`\`\`

## Troubleshooting

- Check logs: \`sudo journalctl -u turtle-dashboard.service -f\`
- Check kiosk logs: \`sudo journalctl -u turtle-kiosk.service -f\`
- Test MQTT connection: \`mosquitto_sub -h $HA_IP -p 9001 -t "turtle/+/+"\`

## Files

- \`index.html\` - Dashboard interface
- \`css/style.css\` - Turtle-themed styling
- \`js/app.js\` - MQTT connection and data handling
- \`start-turtle-kiosk.sh\` - Start script
- \`stop-turtle-kiosk.sh\` - Stop script
- \`status-turtle-kiosk.sh\` - Status script
EOF

# Final status
echo ""
print_status "Turtle Kiosk Dashboard setup complete!"
echo ""
echo "📁 Project directory: $PROJECT_DIR"
echo "🌐 Dashboard URL: http://localhost:8080"
echo "🔌 MQTT Broker: $HA_IP:9001"
echo ""
echo "🚀 To start the dashboard:"
echo "   ./start-turtle-kiosk.sh"
echo ""
echo "🛑 To stop the dashboard:"
echo "   ./stop-turtle-kiosk.sh"
echo ""
echo "📊 To check status:"
echo "   ./status-turtle-kiosk.sh"
echo ""
print_info "The dashboard will auto-start on boot!"
echo ""
print_warning "Make sure your Home Assistant MQTT broker allows connections from this device"
print_warning "and that the turtle sensor topics are being published."
echo ""
print_status "Setup complete! 🐢" 