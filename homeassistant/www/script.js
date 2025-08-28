// ===== TURTX MONITOR DASHBOARD - MAIN SCRIPT =====
// Professional Turtle Life Support Monitoring System

class TurtXMonitor {
    constructor() {
        this.apiBaseUrl = 'http://10.0.20.69/api/';
        this.weatherApiKey = 'YOUR_OPENWEATHER_API_KEY'; // Replace with actual key
        this.weatherLocation = { lat: 45.5152, lon: -122.6784 }; // Portland, OR
        this.currentTheme = 'day';
        this.isConnected = false;
        this.lastData = null;
        this.dataPollingInterval = null;
        this.weatherPollingInterval = null;
        this.logs = [];
        
        this.init();
    }

    // ===== INITIALIZATION =====
    async init() {
        console.log('🐢 Initializing TurtX Monitor...');
        
        // Initialize all systems
        this.initializeTheme();
        this.initializeAnimatedHeader();
        this.initializeWeatherSystem();
        this.initializeLogSystem();
        this.initializeNavigation();
        this.initializeEventListeners();
        
        // Start data polling
        await this.startDataPolling();
        this.startWeatherPolling();
        
        // Hide loading overlay
        setTimeout(() => {
            document.getElementById('loading-overlay').classList.add('hidden');
        }, 2000);
        
        console.log('✅ TurtX Monitor initialized successfully');
    }

    // ===== THEME MANAGEMENT =====
    initializeTheme() {
        const hour = new Date().getHours();
        const isDay = hour >= 6 && hour < 18;
        this.currentTheme = isDay ? 'day' : 'night';
        this.applyTheme(this.currentTheme);
        
        // Theme toggle functionality
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.currentTheme = this.currentTheme === 'day' ? 'night' : 'day';
                this.applyTheme(this.currentTheme);
            });
        }
    }

    applyTheme(theme) {
        document.body.className = `theme-${theme}`;
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'day' ? '🌙' : '☀️';
        }
    }

    // ===== ANIMATED HEADER SYSTEM =====
    initializeAnimatedHeader() {
        this.updateMoonPhase();
        this.updateMoonPosition();
        this.animateStarField();
        this.animateTurtleSprite();
        
        // Update moon position every minute
        setInterval(() => {
            this.updateMoonPosition();
        }, 60000);
    }

    updateMoonPhase() {
        const date = new Date();
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        
        // Calculate moon phase (0-29.5 days)
        const phase = this.calculateMoonPhase(year, month, day);
        const moonElement = document.getElementById('moon');
        
        if (moonElement) {
            // Update moon appearance based on phase
            if (phase < 3.5 || phase > 26.5) {
                moonElement.style.background = 'radial-gradient(circle at 30% 30%, #fff, #ddd)';
            } else if (phase < 10.5) {
                moonElement.style.background = 'radial-gradient(circle at 70% 30%, #fff, #ddd)';
            } else if (phase < 17.5) {
                moonElement.style.background = 'radial-gradient(circle at 50% 50%, #fff, #ddd)';
            } else if (phase < 24.5) {
                moonElement.style.background = 'radial-gradient(circle at 30% 70%, #fff, #ddd)';
            }
        }
    }

    calculateMoonPhase(year, month, day) {
        // Simplified moon phase calculation
        const date = new Date(year, month - 1, day);
        const knownNewMoon = new Date(2000, 0, 6); // Known new moon date
        const daysSinceKnown = (date - knownNewMoon) / (1000 * 60 * 60 * 24);
        return (daysSinceKnown % 29.53058867);
    }

    updateMoonPosition() {
        const date = new Date();
        const hour = date.getHours() + date.getMinutes() / 60;
        
        // Calculate moon position based on time (simplified)
        const moonElements = document.querySelectorAll('.moon');
        moonElements.forEach(moon => {
            const xPos = 20 + (hour / 24) * 60; // Move across 60% of header width
            moon.style.left = `${xPos}%`;
        });
    }

    animateStarField() {
        const starFields = document.querySelectorAll('.star-field');
        starFields.forEach(field => {
            field.style.animation = 'twinkle 4s ease-in-out infinite';
        });
    }

    animateTurtleSprite() {
        const turtles = document.querySelectorAll('.turtle-sprite');
        turtles.forEach(turtle => {
            turtle.style.animation = 'swim 3s ease-in-out infinite';
        });
    }

    updateTurtleExpression(systemHealth) {
        const turtles = document.querySelectorAll('.turtle-sprite');
        turtles.forEach(turtle => {
            if (systemHealth === 'excellent') {
                turtle.textContent = '🐢';
            } else if (systemHealth === 'warning') {
                turtle.textContent = '😐';
            } else {
                turtle.textContent = '😰';
            }
        });
    }

    // ===== WEATHER SYSTEM INTEGRATION =====
    initializeWeatherSystem() {
        this.fetchWeatherData();
    }

    async fetchWeatherData() {
        try {
            // For demo purposes, using mock data
            // In production, replace with actual OpenWeatherMap API call
            const mockWeatherData = {
                temp: 72,
                condition: 'Partly Cloudy',
                wind: 8,
                humidity: 65,
                aqi: 45,
                icon: '🌤️'
            };
            
            this.updateWeatherDisplay(mockWeatherData);
            
            // Real API call would look like:
            // const response = await fetch(
            //     `https://api.openweathermap.org/data/2.5/weather?lat=${this.weatherLocation.lat}&lon=${this.weatherLocation.lon}&appid=${this.weatherApiKey}&units=imperial`
            // );
            // const data = await response.json();
            // this.updateWeatherDisplay(this.formatWeatherData(data));
            
        } catch (error) {
            console.error('Weather fetch error:', error);
            this.handleWeatherError();
        }
    }

    updateWeatherDisplay(weatherData) {
        const iconElement = document.getElementById('weather-icon');
        const tempElement = document.getElementById('weather-temp');
        const conditionElement = document.getElementById('weather-condition');
        const windElement = document.getElementById('weather-wind');
        const humidityElement = document.getElementById('weather-humidity');
        const aqiElement = document.getElementById('weather-aqi');

        if (iconElement) {
            iconElement.textContent = weatherData.icon;
            this.animateWeatherIcon(weatherData.condition);
        }
        if (tempElement) tempElement.textContent = `${weatherData.temp}°F`;
        if (conditionElement) conditionElement.textContent = weatherData.condition;
        if (windElement) windElement.textContent = `${weatherData.wind} mph`;
        if (humidityElement) humidityElement.textContent = `${weatherData.humidity}%`;
        if (aqiElement) aqiElement.textContent = `AQI ${weatherData.aqi}`;
    }

    animateWeatherIcon(condition) {
        const iconElement = document.getElementById('weather-icon');
        if (!iconElement) return;

        // Remove existing animations
        iconElement.style.animation = 'none';
        
        // Apply appropriate animation based on condition
        if (condition.toLowerCase().includes('sunny') || condition.toLowerCase().includes('clear')) {
            iconElement.style.animation = 'weather-sun-rotate 20s linear infinite';
        } else if (condition.toLowerCase().includes('cloud')) {
            iconElement.style.animation = 'weather-cloud-float 3s ease-in-out infinite';
        } else if (condition.toLowerCase().includes('rain')) {
            iconElement.style.animation = 'weather-rain-bounce 1s ease-in-out infinite';
        }
    }

    handleWeatherError() {
        const weatherElements = document.querySelectorAll('.weather-temp, .weather-condition, .weather-details');
        weatherElements.forEach(element => {
            element.textContent = 'Weather unavailable';
            element.style.opacity = '0.5';
        });
    }

    startWeatherPolling() {
        this.weatherPollingInterval = setInterval(() => {
            this.fetchWeatherData();
        }, 600000); // Every 10 minutes
    }

    // ===== DATA FETCHING & API INTEGRATION =====
    async startDataPolling() {
        await this.fetchLatestData();
        this.dataPollingInterval = setInterval(async () => {
            await this.fetchLatestData();
        }, 2000); // Every 2 seconds
    }

    async fetchLatestData() {
        try {
            // For demo purposes, using mock data
            // In production, replace with actual API call
            const mockData = {
                timestamp: new Date().toISOString(),
                basking_area: {
                    temperature: 95.2 + Math.random() * 2 - 1,
                    humidity: 45 + Math.random() * 5 - 2.5,
                    temperature_unit: "F"
                },
                cooling_area: {
                    temperature: 78.5 + Math.random() * 2 - 1,
                    humidity: 65 + Math.random() * 5 - 2.5,
                    temperature_unit: "F"
                },
                system_status: {
                    heater: Math.random() > 0.3 ? "on" : "off",
                    uv_light: Math.random() > 0.2 ? "on" : "off",
                    power: "stable",
                    network: "connected",
                    alerts: Math.random() > 0.8 ? "temperature_warning" : "none"
                }
            };

            this.updateDashboard(mockData);
            this.updateConnectionStatus(true);
            
            // Real API call would look like:
            // const response = await fetch(`${this.apiBaseUrl}latest`);
            // const data = await response.json();
            // this.updateDashboard(data);
            
        } catch (error) {
            console.error('Data fetch error:', error);
            this.updateConnectionStatus(false);
            this.handleGracefulDegradation();
        }
    }

    updateDashboard(data) {
        // Update temperature values
        this.updateValue('basking-temp', `${data.basking_area.temperature.toFixed(1)}°F`);
        this.updateValue('basking-humidity', `${Math.round(data.basking_area.humidity)}%`);
        this.updateValue('cooling-temp', `${data.cooling_area.temperature.toFixed(1)}°F`);
        this.updateValue('cooling-humidity', `${Math.round(data.cooling_area.humidity)}%`);

        // Update chart values
        this.updateValue('chart-basking-temp', `${data.basking_area.temperature.toFixed(1)}°F`);
        this.updateValue('chart-basking-humidity', `${Math.round(data.basking_area.humidity)}%`);
        this.updateValue('chart-cooling-temp', `${data.cooling_area.temperature.toFixed(1)}°F`);
        this.updateValue('chart-cooling-humidity', `${Math.round(data.cooling_area.humidity)}%`);

        // Update system indicators
        this.updateSystemIndicators(data.system_status);

        // Check temperature thresholds
        this.checkTemperatureThresholds(data.basking_area.temperature, 'basking');
        this.checkTemperatureThresholds(data.cooling_area.temperature, 'cooling');

        // Update turtle expression based on system health
        const systemHealth = this.calculateSystemHealth(data.system_status);
        this.updateTurtleExpression(systemHealth);

        // Store last known good data
        this.lastData = data;
    }

    updateValue(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (element && element.textContent !== newValue) {
            const oldValue = element.textContent;
            element.textContent = newValue;
            element.classList.add('data-update-flash');
            setTimeout(() => {
                element.classList.remove('data-update-flash');
            }, 500);
        }
    }

    updateSystemIndicators(status) {
        const indicators = {
            'heater-status': status.heater,
            'uv-status': status.uv_light,
            'power-status': status.power,
            'network-status': status.network,
            'alert-status': status.alerts
        };

        Object.entries(indicators).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                const oldStatus = element.textContent;
                element.textContent = value === 'on' ? 'ON' : value === 'off' ? 'OFF' : value.toUpperCase();
                
                // Update status colors
                element.className = 'indicator-status';
                if (value === 'on' || value === 'stable' || value === 'connected') {
                    element.classList.add('success');
                } else if (value === 'none') {
                    element.classList.add('success');
                } else {
                    element.classList.add('warning');
                }
            }
        });
    }

    checkTemperatureThresholds(temp, zone) {
        const baskingMin = 85;
        const baskingMax = 105;
        const coolingMin = 70;
        const coolingMax = 85;

        let min, max;
        if (zone === 'basking') {
            min = baskingMin;
            max = baskingMax;
        } else {
            min = coolingMin;
            max = coolingMax;
        }

        const statusElement = document.getElementById(`${zone}-status`);
        if (statusElement) {
            if (temp < min || temp > max) {
                statusElement.className = 'status-indicator critical';
                this.showCriticalAlert(`Temperature ${temp.toFixed(1)}°F in ${zone} area is outside safe range!`, 'critical');
            } else if (temp < min + 5 || temp > max - 5) {
                statusElement.className = 'status-indicator warning';
            } else {
                statusElement.className = 'status-indicator';
            }
        }
    }

    calculateSystemHealth(status) {
        const alerts = status.alerts;
        if (alerts === 'none') return 'excellent';
        if (alerts.includes('warning')) return 'warning';
        return 'critical';
    }

    // ===== SMART LOG MANAGEMENT SYSTEM =====
    initializeLogSystem() {
        this.logs = [
            { id: 1, time: '14:32', message: 'UV cycle completed', type: 'success', severity: 'info' },
            { id: 2, time: '13:15', message: 'Temperature check', type: 'success', severity: 'info' },
            { id: 3, time: '12:45', message: 'Motion detected', type: 'info', severity: 'info' },
            { id: 4, time: '12:30', message: 'System startup', type: 'success', severity: 'info' },
            { id: 5, time: '12:00', message: 'Daily maintenance', type: 'info', severity: 'info' },
            { id: 6, time: '11:45', message: 'Humidity check', type: 'success', severity: 'info' }
        ];
        
        this.updateLogDisplay();
        this.updateLogCounters();
    }

    updateLogDisplay(filter = 'all') {
        const logEntries = document.getElementById('log-entries');
        if (!logEntries) return;

        const filteredLogs = filter === 'all' ? 
            this.logs : 
            this.logs.filter(log => log.severity === filter);

        logEntries.innerHTML = '';
        
        filteredLogs.slice(0, 6).forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <span class="log-time">${log.time}</span>
                <span class="log-message">${log.message} ${this.getLogIcon(log.type)}</span>
            `;
            logEntries.appendChild(logEntry);
        });
    }

    getLogIcon(type) {
        const icons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️',
            'critical': '🚨'
        };
        return icons[type] || 'ℹ️';
    }

    updateLogCounters() {
        const filters = ['all', 'critical', 'warning', 'info'];
        filters.forEach(filter => {
            const count = filter === 'all' ? 
                this.logs.length : 
                this.logs.filter(log => log.severity === filter).length;
            
            const filterBtn = document.querySelector(`[data-filter="${filter}"]`);
            if (filterBtn) {
                filterBtn.textContent = filter === 'all' ? 'All' : `${filter.charAt(0).toUpperCase() + filter.slice(1)} (${count})`;
            }
        });
    }

    addLogEntry(message, type = 'info', severity = 'info') {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });
        
        const newLog = {
            id: Date.now(),
            time: time,
            message: message,
            type: type,
            severity: severity
        };
        
        this.logs.unshift(newLog);
        this.logs = this.logs.slice(0, 50); // Keep only last 50 logs
        
        this.updateLogDisplay();
        this.updateLogCounters();
    }

    // ===== NAVIGATION SYSTEM =====
    initializeNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const targetPage = e.currentTarget.getAttribute('data-page');
                this.navigateToPage(targetPage);
            });
        });
    }

    navigateToPage(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Show target page
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.add('active');
        }
        
        // Update navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-page="${pageId}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }

    // ===== EVENT LISTENERS =====
    initializeEventListeners() {
        // Log filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const filter = e.currentTarget.getAttribute('data-filter');
                
                // Update active filter
                filterButtons.forEach(btn => btn.classList.remove('active'));
                e.currentTarget.classList.add('active');
                
                this.updateLogDisplay(filter);
            });
        });

        // Camera controls
        const refreshCamera = document.getElementById('refresh-camera');
        if (refreshCamera) {
            refreshCamera.addEventListener('click', () => {
                this.refreshCameraFeed();
            });
        }

        const cameraSettings = document.getElementById('camera-settings');
        if (cameraSettings) {
            cameraSettings.addEventListener('click', () => {
                this.openCameraSettings();
            });
        }
    }

    // ===== CAMERA SYSTEM =====
    refreshCameraFeed() {
        const video = document.getElementById('camera-video');
        const placeholder = document.getElementById('camera-placeholder');
        
        if (video && placeholder) {
            // Simulate camera refresh
            placeholder.style.display = 'flex';
            video.style.display = 'none';
            
            setTimeout(() => {
                placeholder.style.display = 'none';
                video.style.display = 'block';
            }, 1000);
        }
    }

    openCameraSettings() {
        // Placeholder for camera settings modal
        console.log('Opening camera settings...');
        this.addLogEntry('Camera settings accessed', 'info', 'info');
    }

    // ===== UTILITY FUNCTIONS =====
    updateConnectionStatus(connected) {
        this.isConnected = connected;
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            if (connected) {
                statusElement.classList.remove('offline');
                statusElement.querySelector('.status-text').textContent = 'Connected';
            } else {
                statusElement.classList.add('offline');
                statusElement.querySelector('.status-text').textContent = 'Offline';
            }
        }
    }

    showCriticalAlert(message, severity) {
        console.warn(`Critical Alert: ${message}`);
        this.addLogEntry(message, severity, 'critical');
        
        // Visual alert animation
        const alertIndicator = document.getElementById('alert-indicator');
        if (alertIndicator) {
            alertIndicator.classList.add('critical');
            setTimeout(() => {
                alertIndicator.classList.remove('critical');
            }, 3000);
        }
    }

    handleGracefulDegradation() {
        if (this.lastData) {
            console.log('Using last known good data due to connection issues');
            this.updateDashboard(this.lastData);
        }
    }

    displayLastUpdateTime() {
        const now = new Date();
        console.log(`Last update: ${now.toLocaleTimeString()}`);
    }

    // ===== CLEANUP =====
    destroy() {
        if (this.dataPollingInterval) {
            clearInterval(this.dataPollingInterval);
        }
        if (this.weatherPollingInterval) {
            clearInterval(this.weatherPollingInterval);
        }
    }
}

// ===== INITIALIZE APPLICATION =====
document.addEventListener('DOMContentLoaded', () => {
    window.turtXMonitor = new TurtXMonitor();
});

// ===== GLOBAL UTILITY FUNCTIONS =====
function showDataUpdateAnimation() {
    const elements = document.querySelectorAll('.temp-value, .humidity-value');
    elements.forEach(element => {
        element.classList.add('data-update-flash');
        setTimeout(() => {
            element.classList.remove('data-update-flash');
        }, 500);
    });
}

function animateValueChange(element, oldValue, newValue) {
    if (element && oldValue !== newValue) {
        element.classList.add('data-update-flash');
        setTimeout(() => {
            element.classList.remove('data-update-flash');
        }, 500);
    }
}

// ===== ERROR HANDLING =====
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (window.turtXMonitor) {
        window.turtXMonitor.addLogEntry(`System error: ${event.error.message}`, 'error', 'critical');
    }
});

// ===== PERFORMANCE OPTIMIZATION =====
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        // Handle resize events efficiently
        console.log('Window resized, updating layout...');
    }, 250);
});

// ===== EXPORT FOR TESTING =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TurtXMonitor;
} 