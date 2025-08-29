/* TurtX Professional Monitoring System - Complete JavaScript */

class TurtXMonitoringSystem {
    constructor() {
        this.config = {
            apiBaseUrl: 'http://10.0.20.69/api',
            updateInterval: 2000, // 2 seconds
            weatherUpdateInterval: 600000, // 10 minutes
            location: { lat: 45.5152, lon: -122.6784 }, // Portland, Oregon
            openWeatherApiKey: 'YOUR_API_KEY_HERE' // Replace with actual key
        };

        this.state = {
            currentPage: 'status',
            theme: 'theme-night',
            lastDataUpdate: null,
            connectionStatus: 'connecting',
            sensorData: null,
            weatherData: null,
            activityLog: []
        };

        this.intervals = {
            dataPolling: null,
            weatherPolling: null,
            moonUpdate: null
        };

        this.init();
    }

    async init() {
        console.log('🐢 TurtX Professional Monitoring System Initializing...');
        
        // Initialize all subsystems
        this.initializeThemeSystem();
        this.initializeNavigationSystem();
        this.initializeAnimatedHeader();
        this.initializeWeatherSystem();
        this.initializeLogSystem();
        this.initializeConnectionMonitoring();
        
        // Start data polling
        this.startDataPolling();
        this.startWeatherPolling();
        
        console.log('✅ TurtX System Fully Operational');
    }

    /* ========== THEME MANAGEMENT ========== */
    initializeThemeSystem() {
        this.state.theme = localStorage.getItem('turtx-theme') || 'theme-night';
        this.applyTheme(this.state.theme);
        
        // Auto theme detection based on time
        this.setupAutoTheme();
        
        // Theme toggle button
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }

    applyTheme(theme) {
        document.body.classList.remove('theme-day', 'theme-night');
        document.body.classList.add(theme);
        this.state.theme = theme;
        localStorage.setItem('turtx-theme', theme);
        
        // Update theme toggle icon
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.textContent = theme === 'theme-day' ? '🌙' : '☀️';
        }
    }

    toggleTheme() {
        const newTheme = this.state.theme === 'theme-day' ? 'theme-night' : 'theme-day';
        this.applyTheme(newTheme);
        localStorage.setItem('manual-theme-override', 'true');
    }

    setupAutoTheme() {
        // Auto-switch based on time (6 AM - 7 PM = day theme)
        const hour = new Date().getHours();
        const autoTheme = (hour >= 6 && hour < 19) ? 'theme-day' : 'theme-night';
        
        if (this.state.theme !== autoTheme && !localStorage.getItem('manual-theme-override')) {
            this.applyTheme(autoTheme);
        }
    }

    /* ========== NAVIGATION SYSTEM ========== */
    initializeNavigationSystem() {
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetPage = btn.getAttribute('data-page');
                this.showPage(targetPage);
            });
        });

        // Touch gesture support
        this.initializeTouchNavigation();
    }

    showPage(pageName) {
        if (!['status', 'camera', 'data'].includes(pageName)) return;

        // Update page visibility
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        const targetPage = document.getElementById(`${pageName}-page`);
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // Update navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll(`[data-page="${pageName}"]`).forEach(btn => {
            btn.classList.add('active');
        });

        this.state.currentPage = pageName;
        
        // Page-specific initialization
        if (pageName === 'camera') {
            this.initializeCameraPage();
        } else if (pageName === 'data') {
            this.refreshDataCharts();
        }
    }

    initializeTouchNavigation() {
        let startX = 0;
        let startY = 0;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const deltaX = endX - startX;
            const deltaY = endY - startY;

            // Only trigger if horizontal swipe is primary
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                const pages = ['status', 'camera', 'data'];
                const currentIndex = pages.indexOf(this.state.currentPage);
                
                let newIndex;
                if (deltaX > 0 && currentIndex > 0) {
                    newIndex = currentIndex - 1; // Swipe right = previous page
                } else if (deltaX < 0 && currentIndex < pages.length - 1) {
                    newIndex = currentIndex + 1; // Swipe left = next page
                }
                
                if (newIndex !== undefined) {
                    this.showPage(pages[newIndex]);
                }
            }
        });
    }

    /* ========== LOG MANAGEMENT SYSTEM ========== */
    initializeLogSystem() {
        // Initialize with sample logs
        this.state.activityLog = [
            {
                id: 'init-1',
                timestamp: new Date().toISOString(),
                type: 'info',
                message: 'TurtX Monitoring System started',
                severity: 'info'
            }
        ];

        // Set up filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const filterType = btn.getAttribute('data-filter');
                this.filterLogs(filterType);
                
                // Update active filter
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        this.updateLogDisplay();
    }

    addLogEntry(severity, message, timestamp = new Date().toISOString()) {
        const logEntry = {
            id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            timestamp,
            type: severity,
            message,
            severity
        };

        this.state.activityLog.unshift(logEntry);
        
        // Keep only last 100 entries
        if (this.state.activityLog.length > 100) {
            this.state.activityLog = this.state.activityLog.slice(0, 100);
        }

        this.updateLogDisplay();
        this.updateLogCounters();
    }

    updateLogDisplay() {
        const logContainer = document.getElementById('log-entries');
        if (!logContainer) return;

        // Clear existing entries
        logContainer.innerHTML = '';

        // Show only the 6 most recent entries to fit exactly in viewport
        const recentLogs = this.state.activityLog.slice(0, 6);
        
        recentLogs.forEach(log => {
            const logElement = this.createLogElement(log);
            logContainer.appendChild(logElement);
        });
    }

    createLogElement(log) {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${log.severity}`;
        logEntry.setAttribute('data-log-id', log.id);

        const timeAgo = this.formatTimeAgo(new Date(log.timestamp));
        const icon = this.getLogIcon(log.severity);

        logEntry.innerHTML = `
            <div class="log-time">${timeAgo}</div>
            <div class="log-icon">${icon}</div>
            <div class="log-message">${log.message}</div>
            <div class="log-actions">
                <button class="log-action-btn" onclick="turtxSystem.viewLogDetail('${log.id}')">View</button>
            </div>
        `;

        logEntry.addEventListener('click', () => this.expandLogEntry(log.id));
        return logEntry;
    }

    getLogIcon(severity) {
        const iconMap = {
            critical: '🔴',
            warning: '🟡',
            info: '🔵',
            success: '🟢'
        };
        return iconMap[severity] || '🔵';
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }

    updateLogCounters() {
        const counts = {
            all: this.state.activityLog.length,
            critical: this.state.activityLog.filter(log => log.severity === 'critical').length,
            warning: this.state.activityLog.filter(log => log.severity === 'warning').length,
            info: this.state.activityLog.filter(log => log.severity === 'info').length
        };

        Object.entries(counts).forEach(([type, count]) => {
            const countElement = document.getElementById(`count-${type}`);
            if (countElement) {
                countElement.textContent = count;
            }
        });
    }

    filterLogs(filterType) {
        const logEntries = document.querySelectorAll('.log-entry');
        
        logEntries.forEach(entry => {
            const entryType = entry.classList.contains('critical') ? 'critical' :
                           entry.classList.contains('warning') ? 'warning' :
                           entry.classList.contains('info') ? 'info' : 'info';
            
            if (filterType === 'all' || filterType === entryType) {
                entry.style.display = 'flex';
            } else {
                entry.style.display = 'none';
            }
        });
    }

    expandLogEntry(logId) {
        const log = this.state.activityLog.find(l => l.id === logId);
        if (log) {
            console.log('Log details:', log);
        }
    }

    viewLogDetail(logId) {
        this.expandLogEntry(logId);
    }

    /* ========== CAMERA FUNCTIONALITY ========== */
    initializeCameraPage() {
        const refreshBtn = document.getElementById('refresh-camera');
        const settingsBtn = document.getElementById('camera-settings');
        const fullscreenBtn = document.getElementById('fullscreen-camera');

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshCameraStream());
        }

        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.showCameraSettings());
        }

        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => this.toggleCameraFullscreen());
        }

        this.updateCameraStatus();
    }

    refreshCameraStream() {
        const cameraStream = document.getElementById('camera-stream');
        if (cameraStream) {
            const timestamp = new Date().getTime();
            cameraStream.src = `http://10.0.20.69:8000/api/camera/live?t=${timestamp}`;
            this.addLogEntry('info', 'Camera stream refreshed', new Date().toISOString());
        }
    }

    updateCameraStatus() {
        const statusElement = document.getElementById('stream-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="status-dot"></div>
                <span>STREAMING</span>
            `;
        }
    }

    showCameraSettings() {
        this.addLogEntry('info', 'Camera settings accessed', new Date().toISOString());
    }

    toggleCameraFullscreen() {
        const cameraFeed = document.getElementById('camera-feed');
        if (cameraFeed) {
            if (document.fullscreenElement) {
                document.exitFullscreen();
            } else {
                cameraFeed.requestFullscreen();
            }
        }
    }

    refreshDataCharts() {
        if (this.state.sensorData) {
            const dataPolling = new DataPollingSystem(this);
            dataPolling.updateDataCharts(this.state.sensorData);
        }
    }

    /* ========== UTILITY FUNCTIONS ========== */
    animateValueChange(element) {
        element.classList.add('data-updated');
        setTimeout(() => {
            element.classList.remove('data-updated');
        }, 500);
    }

    hasActiveCriticalAlerts() {
        return this.state.activityLog.some(log => 
            log.severity === 'critical' && 
            new Date() - new Date(log.timestamp) < 300000 // Last 5 minutes
        );
    }

    updateConnectionStatus(status) {
        this.state.connectionStatus = status;
        
        const connectionStatus = document.getElementById('connection-status');
        if (!connectionStatus) return;

        const statusConfig = {
            connecting: { icon: '📡', text: 'Connecting...', visible: true },
            connected: { icon: '✅', text: 'Connected', visible: false },
            error: { icon: '❌', text: 'Connection Error', visible: true },
            offline: { icon: '📶', text: 'Offline', visible: true }
        };

        const config = statusConfig[status];
        if (config) {
            connectionStatus.querySelector('.connection-icon').textContent = config.icon;
            connectionStatus.querySelector('.connection-text').textContent = config.text;
            
            if (config.visible) {
                connectionStatus.classList.add('visible');
                setTimeout(() => {
                    if (this.state.connectionStatus === 'connected') {
                        connectionStatus.classList.remove('visible');
                    }
                }, 3000);
            } else {
                connectionStatus.classList.remove('visible');
            }
        }
    }

    showCriticalAlert(message) {
        const alertOverlay = document.getElementById('critical-alert');
        const alertMessage = document.getElementById('alert-message');
        const alertDismiss = document.getElementById('alert-dismiss');

        if (alertOverlay && alertMessage) {
            alertMessage.textContent = message;
            alertOverlay.classList.add('visible');

            const dismissHandler = () => {
                alertOverlay.classList.remove('visible');
                alertDismiss.removeEventListener('click', dismissHandler);
            };

            alertDismiss.addEventListener('click', dismissHandler);
            setTimeout(dismissHandler, 10000);
        }
    }

    /* ========== INITIALIZATION HELPERS ========== */
    initializeConnectionMonitoring() {
        window.addEventListener('online', () => {
            this.updateConnectionStatus('connected');
            this.addLogEntry('success', 'Network connection restored', new Date().toISOString());
        });

        window.addEventListener('offline', () => {
            this.updateConnectionStatus('offline');
            this.addLogEntry('critical', 'Network connection lost', new Date().toISOString());
        });
    }

    async startWeatherPolling() {
        this.intervals.weatherPolling = setInterval(async () => {
            const weather = new WeatherSystem(this);
            await weather.fetchWeatherData();
        }, this.config.weatherUpdateInterval);
    }

    /* ========== CLEANUP ========== */
    destroy() {
        Object.values(this.intervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });
        console.log('🐢 TurtX System Shutdown Complete');
    }

    /* ========== WEATHER INTEGRATION ========== */
    async initializeWeatherSystem() {
        await this.fetchWeatherData();
    }

    async fetchWeatherData() {
        try {
            // Mock weather data for demo (replace with actual OpenWeatherMap API)
            const mockWeatherData = {
                main: { temp: 72 + Math.random() * 10, humidity: 65 + Math.random() * 20 },
                weather: [{ main: 'Clear', description: 'clear sky', icon: '01d' }],
                wind: { speed: 5.2 + Math.random() * 3 }
            };
            
            this.state.weatherData = mockWeatherData;
            this.updateWeatherDisplay(mockWeatherData);
        } catch (error) {
            console.error('Weather fetch failed:', error);
            this.handleWeatherError();
        }
    }

    updateWeatherDisplay(weatherData) {
        const elements = {
            'weather-temp': `${Math.round(weatherData.main.temp)}°F`,
            'weather-desc': weatherData.weather[0].description,
            'weather-wind': `Wind: ${weatherData.wind.speed.toFixed(1)} mph`,
            'weather-humidity': `Humidity: ${Math.round(weatherData.main.humidity)}%`
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                this.animateValueChange(element);
            }
        });
        
        this.animateWeatherIcon(weatherData.weather[0].main);
    }

    animateWeatherIcon(condition) {
        const iconElement = document.getElementById('weather-icon');
        if (!iconElement) return;
        
        const iconMap = {
            'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 'Snow': '❄️',
            'Thunderstorm': '⛈️', 'Drizzle': '🌦️', 'Mist': '🌫️'
        };
        
        iconElement.textContent = iconMap[condition] || '🌤️';
        iconElement.style.animation = 'weather-float 4s ease-in-out infinite';
    }

    handleWeatherError() {
        const elements = ['weather-temp', 'weather-desc', 'weather-wind', 'weather-humidity'];
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = '--';
        });
        
        const iconElement = document.getElementById('weather-icon');
        if (iconElement) iconElement.textContent = '❓';
    }

    /* ========== DATA POLLING INTEGRATION ========== */
    async startDataPolling() {
        const dataPoller = new DataPollingSystem(this);
        await dataPoller.startDataPolling();
    }

    async updateDashboard(data) {
        const dataPoller = new DataPollingSystem(this);
        await dataPoller.updateDashboard(data);
    }
}

/* ========== DATA POLLING SYSTEM CLASS ========== */
class DataPollingSystem {
    constructor(turtxSystem) {
        this.system = turtxSystem;
    }

    async startDataPolling() {
        this.system.intervals.dataPolling = setInterval(async () => {
            await this.fetchLatestData();
        }, this.system.config.updateInterval);
        
        await this.fetchLatestData();
    }

    async fetchLatestData() {
        try {
            this.system.updateConnectionStatus('connecting');
            
            // Mock data for demo (replace with actual API call)
            const mockData = {
                timestamp: new Date().toISOString(),
                basking_area: {
                    temperature: 95.2 + (Math.random() - 0.5) * 2,
                    humidity: 45 + Math.random() * 5,
                    temperature_unit: 'F'
                },
                cooling_area: {
                    temperature: 78.5 + (Math.random() - 0.5) * 2,
                    humidity: 65 + Math.random() * 10,
                    temperature_unit: 'F'
                },
                system_status: {
                    heater: Math.random() > 0.8 ? 'off' : 'on',
                    uv_light: 'on',
                    power: 'stable',
                    network: 'connected',
                    alerts: this.generateRandomAlert()
                }
            };

            this.system.state.sensorData = mockData;
            this.system.state.lastDataUpdate = new Date();
            
            await this.updateDashboard(mockData);
            this.system.updateConnectionStatus('connected');
            
            this.system.addLogEntry('info', 'Data update completed', mockData.timestamp);
            
        } catch (error) {
            console.error('Data fetch failed:', error);
            this.system.updateConnectionStatus('error');
            this.system.addLogEntry('critical', `Connection failed: ${error.message}`, new Date().toISOString());
        }
    }

    generateRandomAlert() {
        const alerts = ['none', 'none', 'none', 'temperature_high', 'humidity_low'];
        return alerts[Math.floor(Math.random() * alerts.length)];
    }

    async updateDashboard(data) {
        this.updateTemperatureDisplay('basking', data.basking_area);
        this.updateTemperatureDisplay('cooling', data.cooling_area);
        this.updateSystemIndicators(data.system_status);
        
        if (this.system.state.currentPage === 'data') {
            this.updateDataCharts(data);
        }
        
        this.checkCriticalConditions(data);
        this.system.updateTurtleExpression();
        this.updateLastUpdateTime();
    }

    updateTemperatureDisplay(zone, sensorData) {
        const tempElement = document.getElementById(`${zone}-temp`);
        const humidityElement = document.getElementById(`${zone}-humidity`);
        const statusElement = document.getElementById(`${zone}-status`);

        if (tempElement) {
            const oldValue = tempElement.textContent;
            const newValue = sensorData.temperature.toFixed(1);
            
            if (oldValue !== newValue) {
                tempElement.textContent = newValue;
                this.system.animateValueChange(tempElement);
            }
            
            const tempClass = this.getTemperatureClass(sensorData.temperature, zone);
            tempElement.className = `temp-value ${tempClass}`;
        }

        if (humidityElement) {
            const oldValue = humidityElement.textContent;
            const newValue = `${Math.round(sensorData.humidity)}%`;
            
            if (oldValue !== newValue) {
                humidityElement.textContent = newValue;
                this.system.animateValueChange(humidityElement);
            }
        }

        if (statusElement) {
            const status = this.calculateZoneStatus(sensorData.temperature, sensorData.humidity, zone);
            statusElement.className = `status-indicator ${status}`;
        }
    }

    getTemperatureClass(temp, zone) {
        const ranges = {
            basking: { optimal: [92, 98], acceptable: [88, 102] },
            cooling: { optimal: [75, 82], acceptable: [70, 88] }
        };
        
        const range = ranges[zone];
        if (temp >= range.optimal[0] && temp <= range.optimal[1]) return 'temp-optimal';
        if (temp >= range.acceptable[0] && temp <= range.acceptable[1]) return 'temp-acceptable';
        if (temp < range.acceptable[0] || temp > range.acceptable[1]) return 'temp-critical';
        return 'temp-warning';
    }

    calculateZoneStatus(temp, humidity, zone) {
        const tempClass = this.getTemperatureClass(temp, zone);
        const humidityOk = humidity >= 40 && humidity <= 80;
        
        if (tempClass === 'temp-optimal' && humidityOk) return 'status-excellent';
        if (tempClass === 'temp-acceptable' && humidityOk) return 'status-good';
        if (tempClass === 'temp-warning') return 'status-warning';
        return 'status-critical';
    }

    updateSystemIndicators(systemStatus) {
        const indicators = {
            heater: systemStatus.heater === 'on' ? 'status-excellent' : 'status-info',
            uv: systemStatus.uv_light === 'on' ? 'status-excellent' : 'status-warning',
            power: systemStatus.power === 'stable' ? 'status-excellent' : 'status-critical',
            network: systemStatus.network === 'connected' ? 'status-excellent' : 'status-critical',
            alert: systemStatus.alerts === 'none' ? 'status-excellent' : 'status-warning'
        };

        Object.entries(indicators).forEach(([key, statusClass]) => {
            const statusElement = document.getElementById(`${key === 'uv' ? 'uv' : key}-status`);
            if (statusElement) {
                statusElement.className = `indicator-status ${statusClass}`;
                statusElement.textContent = this.getStatusText(key, systemStatus);
            }
        });

        if (systemStatus.alerts !== 'none') {
            this.system.showCriticalAlert(`System Alert: ${systemStatus.alerts.replace('_', ' ').toUpperCase()}`);
        }
    }

    getStatusText(indicator, systemStatus) {
        const statusMap = {
            heater: systemStatus.heater.toUpperCase(),
            uv: systemStatus.uv_light.toUpperCase(),
            power: systemStatus.power.toUpperCase(),
            network: systemStatus.network.toUpperCase(),
            alert: systemStatus.alerts === 'none' ? 'CLEAR' : 'ACTIVE'
        };
        return statusMap[indicator] || 'UNKNOWN';
    }

    updateDataCharts(data) {
        const elements = {
            'chart-basking-temp': `${data.basking_area.temperature.toFixed(1)}°F`,
            'chart-cooling-temp': `${data.cooling_area.temperature.toFixed(1)}°F`,
            'chart-basking-humidity': `${Math.round(data.basking_area.humidity)}%`,
            'chart-cooling-humidity': `${Math.round(data.cooling_area.humidity)}%`
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                this.system.animateValueChange(element);
            }
        });
    }

    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('last-update-time');
        if (lastUpdateElement && this.system.state.lastDataUpdate) {
            lastUpdateElement.textContent = this.formatTimeAgo(this.system.state.lastDataUpdate);
        }
    }

    formatTimeAgo(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);

        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'Just now';
    }

    checkCriticalConditions(data) {
        const criticalTemp = this.checkTemperatureThresholds(data);
        if (criticalTemp) {
            this.system.addLogEntry('critical', criticalTemp, data.timestamp);
        }

        if (data.system_status.power !== 'stable') {
            this.system.showCriticalAlert('⚡ POWER SYSTEM FAILURE - Check power supply immediately!');
            this.system.addLogEntry('critical', 'Power system unstable', data.timestamp);
        }

        if (data.system_status.network !== 'connected') {
            this.system.addLogEntry('warning', 'Network connectivity issues detected', data.timestamp);
        }
    }

    checkTemperatureThresholds(data) {
        const { basking_area, cooling_area } = data;
        
        if (basking_area.temperature < 85 || basking_area.temperature > 105) {
            return `🔥 CRITICAL: Basking temperature ${basking_area.temperature.toFixed(1)}°F is outside safe range (85-105°F)`;
        }
        
        if (cooling_area.temperature < 65 || cooling_area.temperature > 90) {
            return `❄️ CRITICAL: Cool zone temperature ${cooling_area.temperature.toFixed(1)}°F is outside safe range (65-90°F)`;
        }
        
        return null;
    }
}

/* ========== GLOBAL INITIALIZATION ========== */
let turtxSystem;

document.addEventListener('DOMContentLoaded', () => {
    turtxSystem = new TurtXMonitoringSystem();
});

// Handle page visibility changes for optimization
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('🐢 TurtX going to sleep mode');
    } else {
        console.log('🐢 TurtX waking up');
        if (turtxSystem) {
            turtxSystem.fetchLatestData();
        }
    }
});

// Handle window beforeunload for cleanup
window.addEventListener('beforeunload', () => {
    if (turtxSystem) {
        turtxSystem.destroy();
    }
});

// Global error handler
window.addEventListener('error', (event) => {
    console.error('🚨 TurtX System Error:', event.error);
    if (turtxSystem) {
        turtxSystem.addLogEntry('critical', `System error: ${event.message}`, new Date().toISOString());
    }
});

// Export for debugging
window.turtxSystem = turtxSystem;