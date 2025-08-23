class TurtleDashboard {
    constructor() {
        this.isConnected = false;
        this.client = null;
        this.reconnectTimer = null;
        this.updateTimer = null;
        this.lastValues = {};
        
        // Sensor data with null initialization
        this.sensorData = {
            sensor1: { temperature: null, humidity: null, lastUpdate: null },
            sensor2: { temperature: null, humidity: null, lastUpdate: null }
        };
        
        // Configuration
        this.config = {
            mqttBroker: 'ws://10.0.20.69:9001',
            clientId: 'turtle-kiosk-' + Math.random().toString(16).substr(2, 8),
            topics: {
                sensor1Temp: 'turtle/sensors/sensor1/temperature',
                sensor1Hum: 'turtle/sensors/sensor1/humidity',
                sensor2Temp: 'turtle/sensors/sensor2/temperature',
                sensor2Hum: 'turtle/sensors/sensor2/humidity'
            },
            updateInterval: 1000, // Update UI every 1 second
            reconnectDelay: 10000 // Wait 10 seconds before reconnecting
        };
        
        this.startTime = Date.now();
        this.init();
    }
    
    init() {
        console.log('🐢 Initializing Turtle Dashboard...');
        this.initUI();
        this.connectMQTT();
        this.startUIUpdates();
    }
    
    initUI() {
        this.updateConnectionStatus('connecting');
        this.updateTime();
        this.updateUptime();
        
        // Initialize displays with placeholder
        ['sensor1', 'sensor2'].forEach(sensor => {
            ['temperature', 'humidity'].forEach(type => {
                this.updateSensorDisplay(sensor, type, null);
            });
        });
    }
    
    connectMQTT() {
        if (this.client) {
            this.client.end();
            this.client = null;
        }
        
        console.log('🔌 Connecting to MQTT broker:', this.config.mqttBroker);
        
        try {
            this.client = mqtt.connect(this.config.mqttBroker, {
                clientId: this.config.clientId,
                clean: true,
                reconnectPeriod: 0, // Disable auto-reconnect
                connectTimeout: 10000,
                rejectUnauthorized: false
            });
            
            this.client.on('connect', () => {
                console.log('✅ Connected to MQTT broker');
                this.isConnected = true;
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
                this.scheduleReconnect();
            });
            
            this.client.on('close', () => {
                console.log('🔌 MQTT connection closed');
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                this.scheduleReconnect();
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
                    console.error(`❌ Failed to subscribe to ${topic}:`, err);
                } else {
                    console.log(`✅ Subscribed to ${topic}`);
                }
            });
        });
    }
    
    handleMessage(topic, message) {
        try {
            const value = parseFloat(message);
            if (isNaN(value) || value < -50 || value > 100) {
                return; // Ignore invalid values
            }
            
            // Only update if value has actually changed
            const lastValue = this.lastValues[topic];
            if (lastValue !== value) {
                this.lastValues[topic] = value;
                this.processMessage(topic, value);
            }
            
        } catch (error) {
            console.error('❌ Error processing message:', error);
        }
    }
    
    processMessage(topic, value) {
        // Update sensor data based on topic
        if (topic === this.config.topics.sensor1Temp) {
            this.sensorData.sensor1.temperature = value;
            this.sensorData.sensor1.lastUpdate = new Date();
        } else if (topic === this.config.topics.sensor1Hum) {
            this.sensorData.sensor1.humidity = value;
            this.sensorData.sensor1.lastUpdate = new Date();
        } else if (topic === this.config.topics.sensor2Temp) {
            this.sensorData.sensor2.temperature = value;
            this.sensorData.sensor2.lastUpdate = new Date();
        } else if (topic === this.config.topics.sensor2Hum) {
            this.sensorData.sensor2.humidity = value;
            this.sensorData.sensor2.lastUpdate = new Date();
        }
    }
    
    updateSensorDisplay(sensorId, type, value) {
        const elementId = type === 'temperature' ? `temp${sensorId.slice(-1)}` : `hum${sensorId.slice(-1)}`;
        const element = document.getElementById(elementId);
        
        if (element) {
            if (value === null) {
                element.textContent = '--';
                element.style.opacity = '0.5';
            } else {
                element.textContent = value.toFixed(1);
                element.style.opacity = '1';
            }
        }
        
        // Update last update time
        const updateElement = document.getElementById(`update${sensorId.slice(-1)}`);
        if (updateElement) {
            if (value === null) {
                updateElement.textContent = 'No data';
            } else {
                updateElement.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
            }
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
        
        if (!element || !valueElement) return;
        
        if (value === null) {
            element.className = 'status-item unknown';
            valueElement.textContent = '--';
            return;
        }
        
        let status = 'optimal';
        
        if (value < thresholds.optimal.min || value > thresholds.optimal.max) {
            if (value < thresholds.warning.min || value > thresholds.warning.max) {
                status = 'danger';
            } else {
                status = 'warning';
            }
        }
        
        element.className = `status-item ${status}`;
        valueElement.textContent = value.toFixed(1);
    }
    
    updateOverallStatus() {
        const tempStatus = document.getElementById('tempStatus');
        const humStatus = document.getElementById('humStatus');
        const overallStatus = document.getElementById('overallStatus');
        
        if (!tempStatus || !humStatus || !overallStatus) return;
        
        const tempClass = tempStatus.className;
        const humClass = humStatus.className;
        
        let overallClass = 'optimal';
        let overallText = 'All Systems Optimal';
        
        if (tempClass.includes('danger') || humClass.includes('danger')) {
            overallClass = 'danger';
            overallText = 'Critical Conditions';
        } else if (tempClass.includes('warning') || humClass.includes('warning')) {
            overallClass = 'warning';
            overallText = 'Attention Required';
        }
        
        overallStatus.className = `overall-status ${overallClass}`;
        overallStatus.textContent = overallText;
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
        const statusElement = document.getElementById('connectionStatus');
        if (!statusElement) return;
        
        const statusMap = {
            'connecting': { text: 'Connecting...', class: 'connecting' },
            'connected': { text: 'Connected', class: 'connected' },
            'disconnected': { text: 'Disconnected', class: 'disconnected' },
            'reconnecting': { text: 'Reconnecting...', class: 'reconnecting' },
            'error': { text: 'Connection Error', class: 'error' }
        };
        
        const statusInfo = statusMap[status] || statusMap['error'];
        statusElement.textContent = statusInfo.text;
        statusElement.className = `connection-status ${statusInfo.class}`;
    }
    
    updateTime() {
        const timeElement = document.getElementById('currentTime');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleString();
        }
    }
    
    updateUptime() {
        const uptimeElement = document.getElementById('uptime');
        if (uptimeElement) {
            const uptime = Date.now() - this.startTime;
            const hours = Math.floor(uptime / (1000 * 60 * 60));
            const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
            uptimeElement.textContent = `${hours}h ${minutes}m`;
        }
    }
    
    startUIUpdates() {
        // Update UI at fixed intervals instead of on every message
        this.updateTimer = setInterval(() => {
            this.updateTime();
            this.updateUptime();
            
            // Update sensor displays
            ['sensor1', 'sensor2'].forEach(sensor => {
                ['temperature', 'humidity'].forEach(type => {
                    const value = this.sensorData[sensor][type];
                    this.updateSensorDisplay(sensor, type, value);
                });
            });
            
            // Update status and averages
            this.updateStatus();
            this.updateAverages();
        }, this.config.updateInterval);
    }
    
    showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        this.reconnectTimer = setTimeout(() => {
            console.log('🔄 Attempting to reconnect...');
            this.updateConnectionStatus('reconnecting');
            this.connectMQTT();
        }, this.config.reconnectDelay);
    }
    
    // Cleanup method
    destroy() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        if (this.client) {
            this.client.end();
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Starting Turtle Dashboard...');
    window.turtleDashboard = new TurtleDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.turtleDashboard) {
        window.turtleDashboard.destroy();
    }
}); 