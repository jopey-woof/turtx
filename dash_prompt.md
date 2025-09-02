# TurtX Enhanced Development Prompt - Complete System Rebuild

## 🎯 CRITICAL SUCCESS STRATEGY
**START COMPLETELY FRESH** - Delete all existing attempts and follow this prompt exactly for a successful one-shot implementation.

## Project Overview
Create a **professional-grade turtle habitat monitoring dashboard** with an advanced theme system. This monitors a **living creature** - reliability and visual clarity are paramount.

## 🛠️ Cursor Rules (.cursorrules)

```
# TurtX Turtle Monitoring Dashboard Rules

## Project Structure
- dashboard/ - Main web application
- api/ - Backend API code (if needed)
- docs/ - Documentation

## Code Standards
- Use semantic HTML5 with proper accessibility
- CSS: Use modern features (Grid, Flexbox, CSS Custom Properties)
- JavaScript: ES6+ modules, no external dependencies except weather API
- Comments: Explain theme system and critical monitoring logic
- File organization: Separate concerns (theme, data, UI)

## Theme System Requirements
- All themes MUST define the same CSS custom properties
- Theme switching MUST be instant and smooth
- New themes MUST be addable with just CSS
- NEVER hardcode colors - always use CSS custom properties
- Theme persistence in localStorage

## UI/UX Standards
- 100vh viewport - NO SCROLLING EVER
- Mobile-first responsive design
- Touch-friendly interface (min 44px touch targets)
- Loading states for all async operations
- Error states with retry functionality
- Smooth animations (prefer transform/opacity)

## API Integration
- Retry logic for failed requests
- Graceful degradation when API unavailable
- Visual feedback for connection status
- 2-second update interval for sensor data
- 10-minute interval for weather data

## Performance
- Minimize DOM manipulation during theme switches
- Use requestAnimationFrame for smooth animations
- Debounce rapid user interactions
- Optimize for 60fps on theme transitions

## Accessibility
- High contrast theme for vision impairments
- Proper ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Focus indicators

## Code Organization
- Theme system in separate module
- API client as separate module
- Dashboard logic as separate module
- Clear separation between data and presentation
```

## 📁 Complete File Structure

```
turtx-dashboard/
├── .cursorrules              # Cursor IDE rules
├── README.md                 # Project documentation
├── index.html               # Main dashboard page
├── styles/
│   ├── reset.css           # CSS reset/normalize
│   ├── base.css            # Base layout and typography
│   ├── themes.css          # All theme definitions
│   ├── components.css      # Reusable UI components
│   └── animations.css      # Animations and transitions
├── scripts/
│   ├── main.js            # Application entry point
│   ├── theme-manager.js   # Theme system management
│   ├── api-client.js      # API integration layer
│   ├── dashboard-core.js  # Core dashboard functionality
│   └── utils.js           # Utility functions
├── assets/
│   └── icons/            # SVG icons (optional)
└── config/
    └── settings.js       # Configuration constants
```

## 🎨 Enhanced Theme System Architecture

### CSS Custom Properties Structure (Complete Specification)

```css
:root {
    /* Layout Constants (Never change across themes) */
    --header-height: 15vh;
    --sensor-cards-height: 45vh;
    --weather-height: 10vh;
    --system-status-height: 10vh;
    --navigation-height: 20vh;
    
    /* Animation Constants */
    --transition-fast: all 0.15s ease-out;
    --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    
    /* Universal Styling */
    --border-radius: 12px;
    --border-radius-large: 20px;
    --shadow-soft: 0 2px 10px rgba(0, 0, 0, 0.1);
    --shadow-medium: 0 8px 25px rgba(0, 0, 0, 0.15);
    --shadow-strong: 0 15px 35px rgba(0, 0, 0, 0.2);
    
    /* Status Colors (Universal across all themes) */
    --status-excellent: #10B981;
    --status-good: #22C55E;
    --status-warning: #F59E0B;
    --status-critical: #EF4444;
    --status-info: #3B82F6;
    --status-offline: #6B7280;
}

/* THEME TEMPLATE - Every theme MUST define these variables */
.theme-template {
    /* Backgrounds (Required) */
    --bg-body: /* Main page background */;
    --bg-header: /* Animated header gradient */;
    --bg-card-primary: /* Main content cards */;
    --bg-card-secondary: /* Secondary cards/elements */;
    --bg-button: /* Button backgrounds */;
    --bg-button-hover: /* Button hover state */;
    --bg-navigation: /* Bottom navigation */;
    --bg-modal: /* Modal/overlay backgrounds */;
    
    /* Text Colors (Required) */
    --text-primary: /* Main readable text */;
    --text-secondary: /* Secondary/subtitle text */;
    --text-muted: /* Muted/helper text */;
    --text-accent: /* Accent/link text */;
    --text-inverse: /* Text on dark backgrounds */;
    
    /* Accent Colors (Required) */
    --accent-primary: /* Main brand/accent color */;
    --accent-secondary: /* Secondary accent */;
    --accent-gradient: /* Decorative gradients */;
    
    /* Interactive Elements (Required) */
    --border-light: /* Light borders/dividers */;
    --border-medium: /* Standard borders */;
    --border-accent: /* Accent borders */;
    --focus-outline: /* Focus indicator color */;
    
    /* Special Effects (Optional) */
    --glass-bg: /* Glassmorphism backgrounds */;
    --shimmer: /* Loading shimmer effects */;
}
```

### Built-in Theme Collection

```css
/* Professional Day Theme (Default) */
.theme-professional-day {
    --bg-body: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --bg-header: linear-gradient(135deg, #87CEEB 0%, #98D8E8 50%, #B6E5F0 100%);
    --bg-card-primary: rgba(255, 255, 255, 0.95);
    --bg-card-secondary: rgba(248, 250, 252, 0.9);
    --bg-button: #3B82F6;
    --bg-button-hover: #2563EB;
    --bg-navigation: rgba(255, 255, 255, 0.98);
    --bg-modal: rgba(0, 0, 0, 0.75);
    
    --text-primary: #1F2937;
    --text-secondary: #6B7280;
    --text-muted: #9CA3AF;
    --text-accent: #3B82F6;
    --text-inverse: #FFFFFF;
    
    --accent-primary: #3B82F6;
    --accent-secondary: #10B981;
    --accent-gradient: linear-gradient(45deg, #3B82F6, #10B981);
    
    --border-light: rgba(0, 0, 0, 0.1);
    --border-medium: rgba(0, 0, 0, 0.2);
    --border-accent: #3B82F6;
    --focus-outline: #93C5FD;
    
    --glass-bg: rgba(255, 255, 255, 0.25);
}

/* Professional Night Theme */
.theme-professional-night {
    --bg-body: linear-gradient(135deg, #0c4a6e 0%, #1e3a8a 100%);
    --bg-header: linear-gradient(135deg, #0c1445 0%, #1a237e 50%, #000051 100%);
    --bg-card-primary: rgba(30, 41, 59, 0.95);
    --bg-card-secondary: rgba(15, 23, 42, 0.9);
    --bg-button: #60A5FA;
    --bg-button-hover: #3B82F6;
    --bg-navigation: rgba(30, 41, 59, 0.98);
    --bg-modal: rgba(0, 0, 0, 0.85);
    
    --text-primary: #F1F5F9;
    --text-secondary: #CBD5E1;
    --text-muted: #94A3B8;
    --text-accent: #60A5FA;
    --text-inverse: #1F2937;
    
    --accent-primary: #60A5FA;
    --accent-secondary: #34D399;
    --accent-gradient: linear-gradient(45deg, #60A5FA, #34D399);
    
    --border-light: rgba(255, 255, 255, 0.1);
    --border-medium: rgba(255, 255, 255, 0.2);
    --border-accent: #60A5FA;
    --focus-outline: #93C5FD;
    
    --glass-bg: rgba(30, 41, 59, 0.25);
}

/* Ocean Theme */
.theme-ocean {
    --bg-body: linear-gradient(135deg, #006064 0%, #00838f 50%, #0097a7 100%);
    --bg-header: linear-gradient(135deg, #004d40 0%, #00695c 50%, #00796b 100%);
    --bg-card-primary: rgba(224, 247, 250, 0.95);
    --bg-card-secondary: rgba(178, 235, 242, 0.9);
    --bg-button: #00ACC1;
    --bg-button-hover: #0097A7;
    --bg-navigation: rgba(224, 247, 250, 0.98);
    --bg-modal: rgba(0, 77, 64, 0.85);
    
    --text-primary: #004d40;
    --text-secondary: #00695c;
    --text-muted: #00796b;
    --text-accent: #00ACC1;
    --text-inverse: #E0F7FA;
    
    --accent-primary: #00ACC1;
    --accent-secondary: #4DB6AC;
    --accent-gradient: linear-gradient(45deg, #00ACC1, #4DB6AC);
    
    --border-light: rgba(0, 77, 64, 0.1);
    --border-medium: rgba(0, 77, 64, 0.2);
    --border-accent: #00ACC1;
    --focus-outline: #4DD0E1;
    
    --glass-bg: rgba(224, 247, 250, 0.25);
}

/* Forest Theme */
.theme-forest {
    --bg-body: linear-gradient(135deg, #1b4332 0%, #2d5016 50%, #52734d 100%);
    --bg-header: linear-gradient(135deg, #081c15 0%, #1b4332 50%, #2d5016 100%);
    --bg-card-primary: rgba(214, 233, 225, 0.95);
    --bg-card-secondary: rgba(183, 223, 204, 0.9);
    --bg-button: #52B788;
    --bg-button-hover: #40916C;
    --bg-navigation: rgba(214, 233, 225, 0.98);
    --bg-modal: rgba(27, 67, 50, 0.85);
    
    --text-primary: #1b4332;
    --text-secondary: #2d5016;
    --text-muted: #52734d;
    --text-accent: #52B788;
    --text-inverse: #D6E9E1;
    
    --accent-primary: #52B788;
    --accent-secondary: #74C69D;
    --accent-gradient: linear-gradient(45deg, #52B788, #74C69D);
    
    --border-light: rgba(27, 67, 50, 0.1);
    --border-medium: rgba(27, 67, 50, 0.2);
    --border-accent: #52B788;
    --focus-outline: #95D5B2;
    
    --glass-bg: rgba(214, 233, 225, 0.25);
}

/* Sunset Theme */
.theme-sunset {
    --bg-body: linear-gradient(135deg, #c2410c 0%, #ea580c 50%, #fb923c 100%);
    --bg-header: linear-gradient(135deg, #7c2d12 0%, #c2410c 50%, #ea580c 100%);
    --bg-card-primary: rgba(255, 247, 237, 0.95);
    --bg-card-secondary: rgba(254, 215, 170, 0.9);
    --bg-button: #F97316;
    --bg-button-hover: #EA580C;
    --bg-navigation: rgba(255, 247, 237, 0.98);
    --bg-modal: rgba(124, 45, 18, 0.85);
    
    --text-primary: #7c2d12;
    --text-secondary: #c2410c;
    --text-muted: #ea580c;
    --text-accent: #F97316;
    --text-inverse: #FFF7ED;
    
    --accent-primary: #F97316;
    --accent-secondary: #FB923C;
    --accent-gradient: linear-gradient(45deg, #F97316, #FB923C);
    
    --border-light: rgba(124, 45, 18, 0.1);
    --border-medium: rgba(124, 45, 18, 0.2);
    --border-accent: #F97316;
    --focus-outline: #FED7AA;
    
    --glass-bg: rgba(255, 247, 237, 0.25);
}

/* High Contrast (Accessibility) */
.theme-high-contrast {
    --bg-body: #000000;
    --bg-header: #000000;
    --bg-card-primary: #FFFFFF;
    --bg-card-secondary: #F0F0F0;
    --bg-button: #000000;
    --bg-button-hover: #333333;
    --bg-navigation: #FFFFFF;
    --bg-modal: rgba(0, 0, 0, 0.95);
    
    --text-primary: #000000;
    --text-secondary: #333333;
    --text-muted: #666666;
    --text-accent: #0000FF;
    --text-inverse: #FFFFFF;
    
    --accent-primary: #0000FF;
    --accent-secondary: #000000;
    --accent-gradient: linear-gradient(45deg, #0000FF, #000000);
    
    --border-light: #000000;
    --border-medium: #000000;
    --border-accent: #0000FF;
    --focus-outline: #FF0000;
    
    --glass-bg: rgba(255, 255, 255, 0.9);
}
```

## 🚀 Complete JavaScript Architecture

### Theme Manager (Enhanced)

```javascript
// theme-manager.js
export class ThemeManager {
    constructor() {
        this.currentTheme = 'professional-day';
        this.autoThemeEnabled = true;
        this.themes = new Map([
            ['professional-day', { name: 'Professional Day', auto: true }],
            ['professional-night', { name: 'Professional Night', auto: true }],
            ['ocean', { name: 'Ocean', auto: false }],
            ['forest', { name: 'Forest', auto: false }],
            ['sunset', { name: 'Sunset', auto: false }],
            ['high-contrast', { name: 'High Contrast', auto: false }]
        ]);
        
        this.observers = new Set();
        this.init();
    }

    init() {
        this.loadStoredTheme();
        this.setupThemeButtons();
        this.setupAutoTheme();
        this.setupKeyboardShortcuts();
    }

    // Observer pattern for theme changes
    subscribe(callback) {
        this.observers.add(callback);
    }

    unsubscribe(callback) {
        this.observers.delete(callback);
    }

    notify(themeName) {
        this.observers.forEach(callback => callback(themeName));
    }

    switchTheme(themeName, source = 'manual') {
        if (!this.themes.has(themeName)) {
            console.warn(`Theme "${themeName}" not found`);
            return false;
        }

        const previousTheme = this.currentTheme;
        this.currentTheme = themeName;

        // Update DOM
        document.body.className = document.body.className.replace(/theme-\S+/g, '');
        document.body.classList.add(`theme-${themeName}`);

        // Update UI
        this.updateActiveButton(themeName);
        
        // Store preference (unless auto-switching)
        if (source === 'manual') {
            localStorage.setItem('turtx-theme', themeName);
            localStorage.setItem('turtx-auto-theme', 'false');
            this.autoThemeEnabled = false;
        }

        // Notify observers
        this.notify(themeName);

        // Analytics/logging
        console.log(`Theme switched from ${previousTheme} to ${themeName} (${source})`);
        
        return true;
    }

    // Auto theme based on time
    setupAutoTheme() {
        const checkAutoTheme = () => {
            if (!this.autoThemeEnabled) return;

            const hour = new Date().getHours();
            const targetTheme = (hour >= 6 && hour < 20) ? 'professional-day' : 'professional-night';
            
            if (this.currentTheme !== targetTheme) {
                this.switchTheme(targetTheme, 'auto');
            }
        };

        // Check immediately and every minute
        checkAutoTheme();
        setInterval(checkAutoTheme, 60000);
    }

    // Keyboard shortcuts for theme switching
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.altKey) {
                const themeKeys = ['1', '2', '3', '4', '5', '6'];
                const keyIndex = themeKeys.indexOf(e.key);
                
                if (keyIndex !== -1) {
                    const themeNames = Array.from(this.themes.keys());
                    if (themeNames[keyIndex]) {
                        this.switchTheme(themeNames[keyIndex]);
                        e.preventDefault();
                    }
                }
            }
        });
    }

    // Dynamic theme registration
    registerTheme(name, config, cssVariables) {
        this.themes.set(name, config);
        
        // Inject CSS
        const style = document.createElement('style');
        style.id = `theme-${name}`;
        
        let css = `.theme-${name} {\n`;
        for (const [property, value] of Object.entries(cssVariables)) {
            css += `    ${property}: ${value};\n`;
        }
        css += '}\n';
        
        style.textContent = css;
        document.head.appendChild(style);
        
        // Add theme selector button
        this.addThemeButton(name, config.name);
    }

    // Get current theme properties
    getCurrentThemeProperties() {
        const computedStyle = getComputedStyle(document.documentElement);
        const properties = {};
        
        // Get all CSS custom properties for current theme
        const styleSheets = document.styleSheets;
        for (const sheet of styleSheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.selectorText && rule.selectorText.includes(`theme-${this.currentTheme}`)) {
                        const style = rule.style;
                        for (let i = 0; i < style.length; i++) {
                            const prop = style[i];
                            if (prop.startsWith('--')) {
                                properties[prop] = computedStyle.getPropertyValue(prop).trim();
                            }
                        }
                    }
                }
            } catch (e) {
                // Handle CORS issues with external stylesheets
            }
        }
        
        return properties;
    }

    // Load stored theme preference
    loadStoredTheme() {
        const storedTheme = localStorage.getItem('turtx-theme');
        const autoTheme = localStorage.getItem('turtx-auto-theme') !== 'false';
        
        this.autoThemeEnabled = autoTheme;
        
        if (storedTheme && this.themes.has(storedTheme) && !autoTheme) {
            this.switchTheme(storedTheme, 'stored');
        } else {
            // Use auto theme
            this.autoThemeEnabled = true;
            const hour = new Date().getHours();
            const defaultTheme = (hour >= 6 && hour < 20) ? 'professional-day' : 'professional-night';
            this.switchTheme(defaultTheme, 'auto');
        }
    }

    // Theme selector UI management
    updateActiveButton(themeName) {
        document.querySelectorAll('.theme-button').forEach(button => {
            button.classList.remove('active');
        });
        
        const activeButton = document.querySelector(`[data-theme="${themeName}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
    }

    setupThemeButtons() {
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('.theme-button').forEach(button => {
                button.addEventListener('click', () => {
                    const themeName = button.dataset.theme;
                    this.switchTheme(themeName);
                });

                // Preview on hover
                button.addEventListener('mouseenter', () => {
                    this.previewTheme(button.dataset.theme);
                });

                button.addEventListener('mouseleave', () => {
                    this.endPreview();
                });
            });
        });
    }

    // Theme preview functionality
    previewTheme(themeName) {
        if (!this.themes.has(themeName) || themeName === this.currentTheme) return;
        
        document.body.classList.add('theme-preview');
        document.body.classList.add(`theme-${themeName}`);
    }

    endPreview() {
        document.body.classList.remove('theme-preview');
        // Remove all theme classes except current
        document.body.className = document.body.className.replace(/theme-\S+/g, '');
        document.body.classList.add(`theme-${this.currentTheme}`);
    }
}
```

## 🎮 Enhanced Nyan Cat Turtle Animation

```css
/* Enhanced turtle trail animation */
.turtle-header {
    position: relative;
    height: var(--header-height);
    overflow: hidden;
    background: var(--bg-header);
    display: flex;
    align-items: center;
    justify-content: center;
}

.turtle-container {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
}

.turtle-sprite {
    position: absolute;
    left: 50px;
    font-size: 3rem;
    animation: turtle-bob 2s ease-in-out infinite;
    z-index: 10;
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
}

.rainbow-trail {
    position: absolute;
    left: 80px;
    width: 300px;
    height: 60px;
    overflow: hidden;
}

.rainbow-bands {
    position: absolute;
    width: 400px;
    height: 100%;
    background: repeating-linear-gradient(
        90deg,
        #ff0000 0px, #ff0000 20px,
        #ff7700 20px, #ff7700 40px,
        #ffdd00 40px, #ffdd00 60px,
        #00ff00 60px, #00ff00 80px,
        #0077ff 80px, #0077ff 100px,
        #4400ff 100px, #4400ff 120px,
        #ff0088 120px, #ff0088 140px
    );
    animation: rainbow-flow 3s linear infinite;
    opacity: 0.8;
}

.star-trail {
    position: absolute;
    top: -20px;
    left: 100px;
    width: 400px;
    height: 100px;
    overflow: hidden;
    z-index: 5;
}

.star-trail::before {
    content: '✦ ✧ ⋆ ★ ☆ ✦ ✧ ⋆ ★ ☆ ✦ ✧ ⋆ ★ ☆ ✦ ✧ ⋆ ★ ☆';
    position: absolute;
    white-space: nowrap;
    font-size: 1.2rem;
    color: white;
    text-shadow: 
        0 0 5px rgba(255, 255, 255, 0.8),
        0 0 10px rgba(255, 255, 255, 0.6);
    animation: stars-trail 4s linear infinite;
    display: flex;
    align-items: center;
    height: 100%;
}

.star-field {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
}

.star-field::before,
.star-field::after {
    content: '';
    position: absolute;
    width: 2px;
    height: 2px;
    background: white;
    border-radius: 50%;
    box-shadow: 
        20px 10px 0 white,
        40px 30px 0 rgba(255, 255, 255, 0.8),
        70px 20px 0 rgba(255, 255, 255, 0.6),
        90px 40px 0 white,
        120px 15px 0 rgba(255, 255, 255, 0.7),
        150px 35px 0 rgba(255, 255, 255, 0.5),
        180px 25px 0 white,
        220px 45px 0 rgba(255, 255, 255, 0.8),
        250px 18px 0 rgba(255, 255, 255, 0.6),
        280px 38px 0 white;
    animation: stars-twinkle 6s ease-in-out infinite;
}

.star-field::after {
    animation-delay: 3s;
    left: 50px;
}

.header-title {
    position: absolute;
    right: 50px;
    color: var(--text-inverse);
    font-size: 2rem;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

/* Moon phase display */
.moon-phase {
    position: absolute;
    top: 20px;
    right: 20px;
    font-size: 2rem;
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.7));
    animation: moon-glow 4s ease-in-out infinite alternate;
}

/* Animations */
@keyframes turtle-bob {
    0%, 100% { transform: translateY(0) rotateZ(0deg); }
    25% { transform: translateY(-3px) rotateZ(1deg); }
    50% { transform: translateY(0) rotateZ(0deg); }
    75% { transform: translateY(-2px) rotateZ(-1deg); }
}

@keyframes rainbow-flow {
    0% { transform: translateX(0); }
    100% { transform: translateX(-140px); }
}

@keyframes stars-trail {
    0% { transform: translateX(0); }
    100% { transform: translateX(-200px); }
}

@keyframes stars-twinkle {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}

@keyframes moon-glow {
    0% { filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.7)); }
    100% { filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.9)); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .turtle-sprite { font-size: 2rem; left: 20px; }
    .rainbow-trail { width: 200px; left: 50px; }
    .star-trail { left: 70px; width: 250px; }
    .header-title { font-size: 1.5rem; right: 20px; }
}
```

## 📊 API Integration Architecture

### API Client with Enhanced Error Handling

```javascript
// api-client.js
export class APIClient {
    constructor(baseURL = 'http://10.0.20.69/api/', options = {}) {
        this.baseURL = baseURL;
        this.options = {
            timeout: 5000,
            retries: 3,
            retryDelay: 1000,
            ...options
        };
        
        this.isOnline = navigator.onLine;
        this.observers = new Set();
        
        // Monitor connection status
        this.setupConnectionMonitoring();
    }

    // Observer pattern for status changes
    subscribe(callback) {
        this.observers.add(callback);
    }

    notify(event) {
        this.observers.forEach(callback => callback(event));
    }

    async fetchWithRetry(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        let lastError;
        
        for (let attempt = 1; attempt <= this.options.retries; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.options.timeout);
                
                const response = await fetch(url, {
                    ...options,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                // Success - reset connection status if it was down
                if (!this.isOnline) {
                    this.isOnline = true;
                    this.notify({ type: 'connection', status: 'online' });
                }
                
                return data;
                
            } catch (error) {
                lastError = error;
                console.warn(`API attempt ${attempt} failed:`, error.message);
                
                // Don't retry on abort (timeout) or network errors on final attempt
                if (attempt === this.options.retries) {
                    this.isOnline = false;
                    this.notify({ type: 'connection', status: 'offline', error });
                    break;
                }
                
                // Wait before retry
                await new Promise(resolve => setTimeout(resolve, this.options.retryDelay * attempt));
            }
        }
        
        throw lastError;
    }

    // Get latest sensor data
    async getLatestData() {
        return await this.fetchWithRetry('latest');
    }

    // Health check
    async getHealth() {
        return await this.fetchWithRetry('health');
    }

    // Connection monitoring
    setupConnectionMonitoring() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.notify({ type: 'connection', status: 'online' });
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.notify({ type: 'connection', status: 'offline' });
        });
    }

    // Get connection status
    getConnectionStatus() {
        return {
            isOnline: this.isOnline,
            baseURL: this.baseURL
        };
    }
}

// Weather API integration
export class WeatherAPI {
    constructor(apiKey, location = { lat: 45.5152, lon: -122.6784 }) {
        this.apiKey = apiKey;
        this.location = location;
        this.cache = new Map();
        this.cacheTimeout = 10 * 60 * 1000; // 10 minutes
    }

    async getCurrentWeather() {
        const cacheKey = 'current-weather';
        const cached = this.cache.get(cacheKey);
        
        if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
            return cached.data;
        }

        try {
            const url = `https://api.openweathermap.org/data/2.5/weather?lat=${this.location.lat}&lon=${this.location.lon}&appid=${this.apiKey}&units=imperial`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Weather API error: ${response.status}`);
            }
            
            const data = await response.json();
            
            const weatherData = {
                temperature: Math.round(data.main.temp),
                humidity: data.main.humidity,
                condition: data.weather[0].main,
                description: data.weather[0].description,
                windSpeed: Math.round(data.wind.speed),
                windDirection: this.getWindDirection(data.wind.deg),
                icon: data.weather[0].icon,
                timestamp: Date.now()
            };
            
            // Cache the result
            this.cache.set(cacheKey, {
                data: weatherData,
                timestamp: Date.now()
            });
            
            return weatherData;
            
        } catch (error) {
            console.warn('Weather fetch failed:', error);
            // Return cached data if available, even if expired
            const cached = this.cache.get(cacheKey);
            return cached ? cached.data : null;
        }
    }

    getWindDirection(degrees) {
        const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
        return directions[Math.round(degrees / 22.5) % 16];
    }
}
```

## 🎯 Core Dashboard Logic

```javascript
// dashboard-core.js
export class TurtleDashboard {
    constructor(apiClient, weatherAPI, themeManager) {
        this.api = apiClient;
        this.weather = weatherAPI;
        this.theme = themeManager;
        
        this.currentData = null;
        this.currentWeather = null;
        this.isConnected = true;
        this.updateInterval = null;
        this.weatherInterval = null;
        
        this.init();
    }

    async init() {
        // Setup UI elements
        this.setupUIElements();
        
        // Setup data fetching
        this.setupDataFetching();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Initial data fetch
        await this.fetchData();
        await this.fetchWeather();
        
        // Setup moon phase
        this.updateMoonPhase();
        
        console.log('TurtX Dashboard initialized');
    }

    setupUIElements() {
        // Cache DOM elements for performance
        this.elements = {
            baskingTemp: document.getElementById('basking-temp'),
            baskingHumidity: document.getElementById('basking-humidity'),
            coolTemp: document.getElementById('cool-temp'),
            coolHumidity: document.getElementById('cool-humidity'),
            weatherCard: document.getElementById('weather-card'),
            connectionStatus: document.getElementById('connection-status'),
            lastUpdate: document.getElementById('last-update'),
            systemStatus: document.getElementById('system-status'),
            moonPhase: document.getElementById('moon-phase')
        };
    }

    setupDataFetching() {
        // Fetch sensor data every 2 seconds
        this.updateInterval = setInterval(() => {
            this.fetchData();
        }, 2000);

        // Fetch weather every 10 minutes
        this.weatherInterval = setInterval(() => {
            this.fetchWeather();
        }, 10 * 60 * 1000);

        // Update moon phase once per hour
        setInterval(() => {
            this.updateMoonPhase();
        }, 60 * 60 * 1000);
    }

    setupEventListeners() {
        // API connection status
        this.api.subscribe((event) => {
            if (event.type === 'connection') {
                this.handleConnectionChange(event.status === 'online');
            }
        });

        // Theme changes
        this.theme.subscribe((themeName) => {
            this.handleThemeChange(themeName);
        });

        // Page visibility for performance
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseUpdates();
            } else {
                this.resumeUpdates();
            }
        });
    }

    async fetchData() {
        try {
            const data = await this.api.getLatestData();
            this.handleDataUpdate(data);
        } catch (error) {
            this.handleDataError(error);
        }
    }

    async fetchWeather() {
        if (!this.weather) return;
        
        try {
            const weather = await this.weather.getCurrentWeather();
            if (weather) {
                this.handleWeatherUpdate(weather);
            }
        } catch (error) {
            console.warn('Weather update failed:', error);
        }
    }

    handleDataUpdate(data) {
        const previousData = this.currentData;
        this.currentData = data;

        // Update temperature displays with animation
        this.updateTemperatureDisplay('basking', data.basking_area, previousData?.basking_area);
        this.updateTemperatureDisplay('cool', data.cooling_area, previousData?.cooling_area);

        // Update system status
        this.updateSystemStatus(data.system_status);

        // Update connection indicator
        this.updateConnectionStatus(true);

        // Update last update time
        this.updateLastUpdateTime();
    }

    handleDataError(error) {
        console.error('Data fetch error:', error);
        this.updateConnectionStatus(false);
    }

    updateTemperatureDisplay(zone, newData, previousData) {
        const tempElement = this.elements[`${zone}Temp`];
        const humidityElement = this.elements[`${zone}Humidity`];

        if (!tempElement || !humidityElement) return;

        // Temperature update with counting animation
        const newTemp = newData.temperature;
        const prevTemp = previousData?.temperature;

        if (prevTemp !== undefined && Math.abs(newTemp - prevTemp) > 0.1) {
            this.animateValueChange(tempElement, prevTemp, newTemp, '°F');
        } else {
            tempElement.textContent = `${newTemp.toFixed(1)}°F`;
        }

        // Humidity update
        const newHumidity = newData.humidity;
        const prevHumidity = previousData?.humidity;

        if (prevHumidity !== undefined && Math.abs(newHumidity - prevHumidity) > 1) {
            this.animateValueChange(humidityElement, prevHumidity, newHumidity, '%');
        } else {
            humidityElement.textContent = `${newHumidity}%`;
        }

        // Status color based on ideal ranges
        this.updateZoneStatus(zone, newData);
    }

    animateValueChange(element, fromValue, toValue, unit) {
        const duration = 500; // ms
        const startTime = performance.now();
        const difference = toValue - fromValue;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            
            const currentValue = fromValue + (difference * easeProgress);
            element.textContent = `${currentValue.toFixed(1)}${unit}`;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
        
        // Add flash effect
        element.classList.add('value-updated');
        setTimeout(() => element.classList.remove('value-updated'), 300);
    }

    updateZoneStatus(zone, data) {
        const card = document.querySelector(`.${zone}-card`);
        if (!card) return;

        // Remove existing status classes
        card.classList.remove('status-excellent', 'status-good', 'status-warning', 'status-critical');

        // Determine status based on zone type and values
        let status = 'good';
        
        if (zone === 'basking') {
            // Basking area: 85-95°F ideal, 40-60% humidity ideal
            const temp = data.temperature;
            const humidity = data.humidity;
            
            if (temp >= 88 && temp <= 92 && humidity >= 45 && humidity <= 55) {
                status = 'excellent';
            } else if (temp >= 85 && temp <= 95 && humidity >= 40 && humidity <= 60) {
                status = 'good';
            } else if (temp >= 80 && temp <= 100 && humidity >= 30 && humidity <= 70) {
                status = 'warning';
            } else {
                status = 'critical';
            }
        } else {
            // Cool area: 75-85°F ideal, 50-70% humidity ideal
            const temp = data.temperature;
            const humidity = data.humidity;
            
            if (temp >= 78 && temp <= 82 && humidity >= 55 && humidity <= 65) {
                status = 'excellent';
            } else if (temp >= 75 && temp <= 85 && humidity >= 50 && humidity <= 70) {
                status = 'good';
            } else if (temp >= 70 && temp <= 90 && humidity >= 40 && humidity <= 80) {
                status = 'warning';
            } else {
                status = 'critical';
            }
        }

        card.classList.add(`status-${status}`);
    }

    updateSystemStatus(statusData) {
        if (!this.elements.systemStatus) return;

        const indicators = this.elements.systemStatus.querySelectorAll('.status-indicator');
        
        indicators.forEach(indicator => {
            const system = indicator.dataset.system;
            const isActive = statusData[system] === 'on' || statusData[system] === 'stable' || statusData[system] === 'connected';
            
            indicator.classList.toggle('active', isActive);
            indicator.classList.toggle('inactive', !isActive);
        });
    }

    updateConnectionStatus(isConnected) {
        this.isConnected = isConnected;
        
        const statusElement = this.elements.connectionStatus;
        if (statusElement) {
            statusElement.classList.toggle('connected', isConnected);
            statusElement.classList.toggle('disconnected', !isConnected);
            statusElement.textContent = isConnected ? '🟢 Connected' : '🔴 Offline';
        }
    }

    updateLastUpdateTime() {
        if (this.elements.lastUpdate) {
            const now = new Date();
            this.elements.lastUpdate.textContent = `Last updated: ${now.toLocaleTimeString()}`;
        }
    }

    handleWeatherUpdate(weather) {
        this.currentWeather = weather;
        
        if (this.elements.weatherCard) {
            this.elements.weatherCard.innerHTML = `
                <div class="weather-content">
                    <span class="weather-icon">${this.getWeatherEmoji(weather.condition)}</span>
                    <span class="weather-temp">${weather.temperature}°F</span>
                    <span class="weather-desc">${weather.description}</span>
                    <span class="weather-wind">${weather.windSpeed} mph ${weather.windDirection}</span>
                </div>
            `;
        }
    }

    getWeatherEmoji(condition) {
        const emojiMap = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️',
            'Haze': '🌫️'
        };
        return emojiMap[condition] || '🌤️';
    }

    updateMoonPhase() {
        if (!this.elements.moonPhase) return;

        const phase = this.calculateMoonPhase();
        this.elements.moonPhase.textContent = this.getMoonEmoji(phase);
    }

    calculateMoonPhase() {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        const day = now.getDate();
        
        // Simplified moon phase calculation
        const c = Math.floor(365.25 * year);
        const e = Math.floor(30.6 * month);
        const jd = c + e + day - 694039.09;
        const phase = (jd / 29.5305882) % 1;
        
        return phase;
    }

    getMoonEmoji(phase) {
        if (phase < 0.0625) return '🌑'; // New Moon
        if (phase < 0.1875) return '🌒'; // Waxing Crescent
        if (phase < 0.3125) return '🌓'; // First Quarter
        if (phase < 0.4375) return '🌔'; // Waxing Gibbous
        if (phase < 0.5625) return '🌕'; // Full Moon
        if (phase < 0.6875) return '🌖'; // Waning Gibbous
        if (phase < 0.8125) return '🌗'; // Last Quarter
        return '🌘'; // Waning Crescent
    }

    handleConnectionChange(isOnline) {
        this.updateConnectionStatus(isOnline);
        
        if (isOnline) {
            // Immediately fetch data when connection is restored
            this.fetchData();
        }
    }

    handleThemeChange(themeName) {
        // Update any theme-specific elements
        console.log(`Dashboard theme changed to: ${themeName}`);
        
        // Trigger any theme-specific animations or adjustments
        this.triggerThemeTransition();
    }

    triggerThemeTransition() {
        // Add smooth transition class temporarily
        document.body.classList.add('theme-transitioning');
        
        setTimeout(() => {
            document.body.classList.remove('theme-transitioning');
        }, 500);
    }

    pauseUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    resumeUpdates() {
        if (!this.updateInterval) {
            this.setupDataFetching();
            this.fetchData(); // Immediate fetch
        }
    }

    // Cleanup method
    destroy() {
        if (this.updateInterval) clearInterval(this.updateInterval);
        if (this.weatherInterval) clearInterval(this.weatherInterval);
    }
}
```

## 🎨 Complete HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="TurtX - Professional Turtle Habitat Monitoring Dashboard">
    <title>TurtX Monitor</title>
    
    <!-- Styles -->
    <link rel="stylesheet" href="styles/reset.css">
    <link rel="stylesheet" href="styles/base.css">
    <link rel="stylesheet" href="styles/themes.css">
    <link rel="stylesheet" href="styles/components.css">
    <link rel="stylesheet" href="styles/animations.css">
    
    <!-- PWA manifest -->
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#3B82F6">
    
    <!-- Icons -->
    <link rel="icon" type="image/svg+xml" href="assets/icons/turtle.svg">
    <link rel="apple-touch-icon" href="assets/icons/turtle-180.png">
</head>
<body class="theme-professional-day">
    <!-- Loading Screen -->
    <div id="loading-screen" class="loading-screen">
        <div class="loading-content">
            <div class="loading-turtle">🐢</div>
            <div class="loading-text">Loading TurtX...</div>
        </div>
    </div>

    <!-- Main Dashboard -->
    <main id="dashboard" class="dashboard">
        <!-- Animated Header -->
        <header class="turtle-header">
            <div class="turtle-container">
                <div class="star-field"></div>
                <div class="turtle-sprite">🐢</div>
                <div class="rainbow-trail">
                    <div class="rainbow-bands"></div>
                </div>
                <div class="star-trail"></div>
                <div class="header-title">TurtX Monitor</div>
                <div id="moon-phase" class="moon-phase">🌕</div>
            </div>
        </header>

        <!-- Sensor Data Cards -->
        <section class="sensor-section">
            <div class="sensor-cards">
                <!-- Basking Area Card -->
                <div class="sensor-card basking-card">
                    <div class="card-header">
                        <span class="card-icon">🔥</span>
                        <h2>Basking Area</h2>
                    </div>
                    <div class="card-content">
                        <div class="sensor-reading">
                            <div class="reading-value">
                                <span id="basking-temp" class="temperature-value">--.-°F</span>
                            </div>
                            <div class="reading-label">Temperature</div>
                        </div>
                        <div class="sensor-reading">
                            <div class="reading-value">
                                <span id="basking-humidity" class="humidity-value">--%</span>
                            </div>
                            <div class="reading-label">Humidity</div>
                        </div>
                    </div>
                    <div class="card-status">
                        <div class="status-indicator" data-zone="basking"></div>
                    </div>
                </div>

                <!-- Cool Area Card -->
                <div class="sensor-card cool-card">
                    <div class="card-header">
                        <span class="card-icon">❄️</span>
                        <h2>Cool Side</h2>
                    </div>
                    <div class="card-content">
                        <div class="sensor-reading">
                            <div class="reading-value">
                                <span id="cool-temp" class="temperature-value">--.-°F</span>
                            </div>
                            <div class="reading-label">Temperature</div>
                        </div>
                        <div class="sensor-reading">
                            <div class="reading-value">
                                <span id="cool-humidity" class="humidity-value">--%</span>
                            </div>
                            <div class="reading-label">Humidity</div>
                        </div>
                    </div>
                    <div class="card-status">
                        <div class="status-indicator" data-zone="cool"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Weather Card -->
        <section class="weather-section">
            <div id="weather-card" class="weather-card">
                <div class="weather-content">
                    <span class="weather-icon">🌤️</span>
                    <span class="weather-temp">--°F</span>
                    <span class="weather-desc">Loading...</span>
                    <span class="weather-wind">-- mph --</span>
                </div>
            </div>
        </section>

        <!-- System Status -->
        <section class="system-section">
            <div id="system-status" class="system-status">
                <div class="status-indicator" data-system="heater" title="Heater">
                    <span class="indicator-icon">🌡️</span>
                    <span class="indicator-label">Heat</span>
                </div>
                <div class="status-indicator" data-system="uv_light" title="UV Light">
                    <span class="indicator-icon">💡</span>
                    <span class="indicator-label">UV</span>
                </div>
                <div class="status-indicator" data-system="power" title="Power">
                    <span class="indicator-icon">⚡</span>
                    <span class="indicator-label">Power</span>
                </div>
                <div class="status-indicator" data-system="network" title="Network">
                    <span class="indicator-icon">📡</span>
                    <span class="indicator-label">Net</span>
                </div>
                <div id="connection-status" class="connection-status">
                    🟡 Connecting...
                </div>
            </div>
        </section>

        <!-- Navigation & Theme Selector -->
        <nav class="navigation">
            <div class="nav-content">
                <div class="nav-buttons">
                    <button class="nav-button active" data-page="status">
                        <span class="nav-icon">📊</span>
                        <span class="nav-label">Status</span>
                    </button>
                    <button class="nav-button" data-page="camera">
                        <span class="nav-icon">📷</span>
                        <span class="nav-label">Camera</span>
                    </button>
                    <button class="nav-button" data-page="data">
                        <span class="nav-icon">📈</span>
                        <span class="nav-label">Data</span>
                    </button>
                </div>
                
                <div class="theme-selector">
                    <div class="theme-label">Themes:</div>
                    <div class="theme-buttons">
                        <button class="theme-button theme-professional-day-btn active" 
                                data-theme="professional-day" 
                                title="Professional Day"
                                aria-label="Professional Day Theme"></button>
                        <button class="theme-button theme-professional-night-btn" 
                                data-theme="professional-night" 
                                title="Professional Night"
                                aria-label="Professional Night Theme"></button>
                        <button class="theme-button theme-ocean-btn" 
                                data-theme="ocean" 
                                title="Ocean Theme"
                                aria-label="Ocean Theme"></button>
                        <button class="theme-button theme-forest-btn" 
                                data-theme="forest" 
                                title="Forest Theme"
                                aria-label="Forest Theme"></button>
                        <button class="theme-button theme-sunset-btn" 
                                data-theme="sunset" 
                                title="Sunset Theme"
                                aria-label="Sunset Theme"></button>
                        <button class="theme-button theme-high-contrast-btn" 
                                data-theme="high-contrast" 
                                title="High Contrast"
                                aria-label="High Contrast Theme"></button>
                    </div>
                </div>
                
                <div class="status-info">
                    <div id="last-update" class="last-update">Last updated: --:--:--</div>
                </div>
            </div>
        </nav>
    </main>

    <!-- Configuration -->
    <script src="config/settings.js"></script>
    <!-- Core Scripts -->
    <script type="module" src="scripts/main.js"></script>
</body>
</html>
```

## ⚙️ Configuration & Settings

```javascript
// config/settings.js
window.TURTX_CONFIG = {
    api: {
        baseURL: 'http://10.0.20.69/api/',
        timeout: 5000,
        retries: 3,
        retryDelay: 1000,
        updateInterval: 2000, // 2 seconds
    },
    
    weather: {
        apiKey: 'YOUR_OPENWEATHERMAP_API_KEY', // Replace with actual key
        location: {
            lat: 45.5152,
            lon: -122.6784,
            name: 'Portland, OR'
        },
        updateInterval: 600000, // 10 minutes
    },
    
    temperature: {
        unit: 'F', // F or C
        basking: {
            ideal: { min: 88, max: 92 },
            acceptable: { min: 85, max: 95 },
            critical: { min: 80, max: 100 }
        },
        cooling: {
            ideal: { min: 78, max: 82 },
            acceptable: { min: 75, max: 85 },
            critical: { min: 70, max: 90 }
        }
    },
    
    humidity: {
        basking: {
            ideal: { min: 45, max: 55 },
            acceptable: { min: 40, max: 60 },
            critical: { min: 30, max: 70 }
        },
        cooling: {
            ideal: { min: 55, max: 65 },
            acceptable: { min: 50, max: 70 },
            critical: { min: 40, max: 80 }
        }
    },
    
    ui: {
        animationDuration: 500,
        theme: {
            autoSwitch: true,
            dayTheme: 'professional-day',
            nightTheme: 'professional-night',
            dayStart: 6, // 6 AM
            nightStart: 20 // 8 PM
        }
    }
};
```

## 🚀 Main Application Entry Point

```javascript
// scripts/main.js
import { ThemeManager } from './theme-manager.js';
import { APIClient, WeatherAPI } from './api-client.js';
import { TurtleDashboard } from './dashboard-core.js';

class TurtXApp {
    constructor() {
        this.themeManager = null;
        this.apiClient = null;
        this.weatherAPI = null;
        this.dashboard = null;
        this.isInitialized = false;
    }

    async init() {
        try {
            console.log('🐢 Initializing TurtX Dashboard...');
            
            // Show loading screen
            this.showLoadingScreen();
            
            // Initialize core systems
            await this.initializeCore();
            
            // Initialize dashboard
            await this.initializeDashboard();
            
            // Hide loading screen
            this.hideLoadingScreen();
            
            this.isInitialized = true;
            console.log('✅ TurtX Dashboard ready!');
            
        } catch (error) {
            console.error('❌ Failed to initialize TurtX:', error);
            this.showErrorScreen(error);
        }
    }

    async initializeCore() {
        // Get configuration
        const config = window.TURTX_CONFIG || {};
        
        // Initialize theme manager
        this.themeManager = new ThemeManager();
        
        // Initialize API client
        this.apiClient = new APIClient(
            config.api?.baseURL || 'http://10.0.20.69/api/',
            config.api
        );
        
        // Initialize weather API (if API key provided)
        if (config.weather?.apiKey) {
            this.weatherAPI = new WeatherAPI(
                config.weather.apiKey,
                config.weather.location
            );
        } else {
            console.warn('⚠️ No weather API key provided');
        }
    }

    async initializeDashboard() {
        // Create dashboard instance
        this.dashboard = new TurtleDashboard(
            this.apiClient,
            this.weatherAPI,
            this.themeManager
        );
        
        // Setup global error handling
        this.setupErrorHandling();
        
        // Setup service worker for PWA (optional)
        this.setupServiceWorker();
    }

    showLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.display = 'flex';
        }
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 300);
        }
    }

    showErrorScreen(error) {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.innerHTML = `
                <div class="error-content">
                    <div class="error-icon">⚠️</div>
                    <div class="error-title">Failed to Initialize</div>
                    <div class="error-message">${error.message}</div>
                    <button onclick="location.reload()" class="retry-button">Retry</button>
                </div>
            `;
        }
    }

    setupErrorHandling() {
        // Global error handler
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.handleError(event.error);
        });

        // Promise rejection handler
        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.handleError(event.reason);
        });
    }

    handleError(error) {
        // Show user-friendly error notification
        this.showNotification(`Error: ${error.message}`, 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    async setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/sw.js');
                console.log('✅ Service worker registered');
            } catch (error) {
                console.warn('⚠️ Service worker registration failed:', error);
            }
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new TurtXApp();
    app.init();
    
    // Make app available globally for debugging
    window.TurtXApp = app;
});

// Handle PWA install prompt
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    deferredPrompt = e;
    // Show install button if desired
});
```

## 🎨 Enhanced Component Styles

```css
/* styles/components.css */

/* Loading Screen */
.loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: var(--bg-body);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    transition: opacity var(--transition-smooth);
}

.loading-content,
.error-content {
    text-align: center;
    color: var(--text-primary);
}

.loading-turtle {
    font-size: 4rem;
    animation: turtle-bob 2s ease-in-out infinite;
    margin-bottom: 1rem;
}

.loading-text,
.error-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.error-message {
    color: var(--text-secondary);
    margin-bottom: 2rem;
    max-width: 400px;
}

.retry-button {
    background: var(--accent-primary);
    color: var(--text-inverse);
    border: none;
    padding: 12px 24px;
    border-radius: var(--border-radius);
    font-size: 1rem;
    cursor: pointer;
    transition: var(--transition-smooth);
}

.retry-button:hover {
    background: var(--bg-button-hover);
    transform: translateY(-2px);
}

/* Dashboard Layout */
.dashboard {
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: var(--bg-body);
    overflow: hidden;
}

/* Sensor Cards */
.sensor-section {
    height: var(--sensor-cards-height);
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.sensor-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    width: 100%;
    max-width: 800px;
    height: 100%;
}

.sensor-card {
    background: var(--bg-card-primary);
    border-radius: var(--border-radius-large);
    box-shadow: var(--shadow-medium);
    border: 2px solid var(--border-light);
    display: flex;
    flex-direction: column;
    transition: var(--transition-smooth);
    overflow: hidden;
    position: relative;
}

.sensor-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--accent-primary);
    opacity: 0;
    transition: var(--transition-smooth);
}

.sensor-card.status-excellent::before { 
    background: var(--status-excellent); 
    opacity: 1; 
}

.sensor-card.status-good::before { 
    background: var(--status-good); 
    opacity: 1; 
}

.sensor-card.status-warning::before { 
    background: var(--status-warning); 
    opacity: 1; 
}

.sensor-card.status-critical::before { 
    background: var(--status-critical); 
    opacity: 1; 
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1.5rem 1.5rem 1rem;
    background: var(--bg-card-secondary);
}

.card-icon {
    font-size: 1.5rem;
}

.card-header h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
}

.card-content {
    flex: 1;
    padding: 1rem 1.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1.5rem;
}

.sensor-reading {
    text-align: center;
}

.reading-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.reading-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
}

.card-status {
    padding: 1rem;
    display: flex;
    justify-content: center;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--status-offline);
    transition: var(--transition-smooth);
}

/* Value update animation */
.value-updated {
    animation: value-flash 0.3s ease-out;
}

@keyframes value-flash {
    0% { background: rgba(59, 130, 246, 0.2); }
    100% { background: transparent; }
}

/* Weather Section */
.weather-section {
    height: var(--weather-height);
    padding: 0 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.weather-card {
    background: var(--bg-card-primary);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-soft);
    border: 1px solid var(--border-light);
    width: 100%;
    max-width: 600px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition-smooth);
}

.weather-content {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: var(--text-primary);
}

.weather-icon {
    font-size: 1.5rem;
}

.weather-temp {
    font-size: 1.25rem;
    font-weight: 600;
}

.weather-desc {
    font-size: 1rem;
    color: var(--text-secondary);
    text-transform: capitalize;
}

.weather-wind {
    font-size: 0.875rem;
    color: var(--text-muted);
}

/* System Status */
.system-section {
    height: var(--system-status-height);
    padding: 0 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.system-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    width: 100%;
    max-width: 600px;
}

.status-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    opacity: 0.5;
    transition: var(--transition-smooth);
    cursor: help;
}

.status-indicator.active {
    opacity: 1;
    color: var(--status-good);
}

.status-indicator.inactive {
    opacity: 0.3;
    color: var(--status-offline);
}

.indicator-icon {
    font-size: 1.5rem;
}

.indicator-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.connection-status {
    font-size: 0.875rem;
    padding: 0.25rem 0.75rem;
    border-radius: var(--border-radius);
    background: var(--bg-card-secondary);
    transition: var(--transition-smooth);
}

.connection-status.connected {
    color: var(--status-good);
}

.connection-status.disconnected {
    color: var(--status-critical);
    animation: connection-pulse 2s ease-in-out infinite;
}

@keyframes connection-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Navigation */
.navigation {
    height: var(--navigation-height);
    background: var(--bg-navigation);
    border-top: 1px solid var(--border-light);
    display: flex;
    align-items: center;
    padding: 1rem;
}

.nav-content {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 2rem;
}

.nav-buttons {
    display: flex;
    gap: 1rem;
}

.nav-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.75rem 1rem;
    background: transparent;
    border: 2px solid transparent;
    border-radius: var(--border-radius);
    cursor: pointer;
    transition: var(--transition-smooth);
    color: var(--text-secondary);
    min-width: 80px;
}

.nav-button:hover {
    background: var(--bg-card-secondary);
    color: var(--text-primary);
}

.nav-button.active {
    background: var(--accent-primary);
    color: var(--text-inverse);
    border-color: var(--accent-primary);
}

.nav-icon {
    font-size: 1.25rem;
}

.nav-label {
    font-size: 0.75rem;
    font-weight: 500;
}

/* Theme Selector */
.theme-selector {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

.theme-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
}

.theme-buttons {
    display: flex;
    gap: 0.5rem;
}

.theme-button {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: 2px solid var(--border-light);
    cursor: pointer;
    transition: var(--transition-smooth);
    position: relative;
    overflow: hidden;
}

.theme-button:hover {
    transform: scale(1.1);
    box-shadow: var(--shadow-medium);
}

.theme-button.active {
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 2px var(--accent-primary);
}

/* Theme button specific styles */
.theme-professional-day-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.theme-professional-night-btn {
    background: linear-gradient(135deg, #0c4a6e 0%, #1e3a8a 100%);
}

.theme-ocean-btn {
    background: linear-gradient(135deg, #006064 0%, #0097a7 100%);
}

.theme-forest-btn {
    background: linear-gradient(135deg, #1b4332 0%, #52734d 100%);
}

.theme-sunset-btn {
    background: linear-gradient(135deg, #c2410c 0%, #fb923c 100%);
}

.theme-high-contrast-btn {
    background: linear-gradient(45deg, #000000 50%, #ffffff 50%);
}

/* Status Info */
.status-info {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.25rem;
}

.last-update {
    font-size: 0.75rem;
    color: var(--text-muted);
}

/* Notifications */
.notification {
    position: fixed;
    top: 2rem;
    right: 2rem;
    padding: 1rem 1.5rem;
    border-radius: var(--border-radius);
    background: var(--bg-card-primary);
    border: 1px solid var(--border-medium);
    box-shadow: var(--shadow-strong);
    z-index: 1000;
    animation: notification-slide-in 0.3s ease-out;
}

.notification-error {
    border-left: 4px solid var(--status-critical);
    color: var(--status-critical);
}

.notification-success {
    border-left: 4px solid var(--status-good);
    color: var(--status-good);
}

.notification-info {
    border-left: 4px solid var(--status-info);
    color: var(--status-info);
}

@keyframes notification-slide-in {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .sensor-cards {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .nav-content {
        grid-template-columns: 1fr;
        gap: 1rem;
        text-align: center;
    }
    
    .theme-buttons {
        justify-content: center;
    }
    
    .reading-value {
        font-size: 2rem;
    }
    
    .system-status {
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .sensor-section,
    .weather-section,
    .system-section,
    .navigation {
        padding: 0.5rem;
    }
    
    .card-header {
        padding: 1rem;
    }
    
    .card-content {
        padding: 0.5rem 1rem 1rem;
    }
    
    .reading-value {
        font-size: 1.75rem;
    }
    
    .nav-buttons {
        justify-content: center;
        width: 100%;
    }
}

/* Theme Transition Effects */
.theme-transitioning * {
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* High Contrast Accessibility Overrides */
.theme-high-contrast .sensor-card {
    border-width: 3px;
}

.theme-high-contrast .theme-button {
    border-width: 3px;
}

.theme-high-contrast .nav-button.active {
    background: var(--text-primary);
    color: var(--bg-card-primary);
}

/* Print Styles */
@media print {
    .navigation,
    .theme-selector {
        display: none;
    }
    
    .dashboard {
        height: auto;
    }
    
    .sensor-section {
        height: auto;
    }
}
```

## 🔄 Service Worker (PWA Support)

```javascript
// sw.js
const CACHE_NAME = 'turtx-dashboard-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/styles/reset.css',
    '/styles/base.css',
    '/styles/themes.css',
    '/styles/components.css',
    '/styles/animations.css',
    '/scripts/main.js',
    '/scripts/theme-manager.js',
    '/scripts/api-client.js',
    '/scripts/dashboard-core.js',
    '/config/settings.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            }
        )
    );
});
```

## 📱 PWA Manifest

```json
{
    "name": "TurtX Dashboard",
    "short_name": "TurtX",
    "description": "Professional turtle habitat monitoring dashboard",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#667eea",
    "theme_color": "#3B82F6",
    "icons": [
        {
            "src": "assets/icons/turtle-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "assets/icons/turtle-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ],
    "categories": ["productivity", "utilities"],
    "lang": "en",
    "orientation": "portrait"
}
```

## 🚀 Implementation Steps

### Phase 1: Foundation (30 minutes)
1. Create file structure exactly as specified
2. Set up base HTML with proper viewport and meta tags
3. Implement CSS custom properties system with all 6 themes
4. Create basic theme switching functionality

### Phase 2: Core Dashboard (45 minutes)
1. Implement API client with retry logic and error handling
2. Build sensor data display with real-time updates
3. Add weather integration with caching
4. Create system status indicators

### Phase 3: Animations & Polish (30 minutes)
1. Implement Nyan Cat turtle animation with rainbow trail
2. Add moon phase calculation and display
3. Create smooth theme transitions
4. Add value change animations

### Phase 4: Testing & Optimization (15 minutes)
1. Test all themes on different screen sizes
2. Verify 100vh layout with no scrolling
3. Test API error handling and reconnection
4. Ensure smooth 60fps animations

## ✅ Success Criteria Checklist

- [ ] **Zero Scrolling**: All content fits perfectly in 100vh on all themes
- [ ] **Smooth Theme Switching**: Instant theme changes with smooth transitions
- [ ] **Reliable API Integration**: Robust error handling and retry logic
- [ ] **Beautiful Animations**: 60fps Nyan Cat turtle with authentic rainbow trail
- [ ] **Professional Design**: Medical-grade monitoring interface
- [ ] **Accessibility**: High contrast theme meets WCAG standards
- [ ] **Responsive Design**: Works perfectly on mobile and desktop
- [ ] **Extensible Architecture**: Easy to add new themes and features
- [ ] **Real-time Updates**: 2-second sensor updates with visual feedback
- [ ] **Weather Integration**: Portland, OR weather with animated icons

## 🎯 One-Shot Implementation Strategy

This prompt is designed for **cursor/AI-assisted development** with the following approach:

1. **Start completely fresh** - delete all existing code
2. **Follow the exact file structure** provided
3. **Copy-paste the configuration** as-is to avoid typing errors
4. **Implement features in order** - foundation first, then polish
5. **Use the provided CSS custom properties exactly** to ensure theme consistency
6. **Test each theme immediately** after implementation

The result will be a **stunning, professional-grade turtle monitoring dashboard** with:
- ✨ Beautiful design that makes users say "wow"
- 🔄 Seamless theme switching between 6 professionally designed themes  
- 📊 Rock-solid monitoring capabilities worthy of life-support systems
- 🎮 Delightful Nyan Cat animations that bring joy without compromising functionality
- 🏥 Medical-grade reliability with graceful error handling
- ♿ Full accessibility support including high-contrast mode
- 📱 Perfect responsive design for all devices

**This is your complete, production-ready implementation guide. Follow it exactly for guaranteed success!**