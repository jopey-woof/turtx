# TurtX Multi-Page Kiosk Dashboard with Advanced Theme System - Cursor Development Prompt

## Project Overview
**FIRST**: Clean up any existing messy implementation attempts. Delete previous broken code and start fresh with a proper structure.

Create a **beautiful, professional-grade** turtle monitoring dashboard for a **living creature** with an **extensible theme system** - where reliability and immediate visual feedback are paramount. This is not just a display, it's a life-support monitoring system that must be both stunning and functionally perfect.

## Design Philosophy - LIVING CREATURE MONITORING + THEME FLEXIBILITY
- **Beauty with Purpose**: Elegant design that enhances monitoring efficiency
- **Professional Medical/Scientific Grade**: Clean, trustworthy interface design
- **Reliability First**: System must never fail to display critical information
- **Immediate Visual Feedback**: Instant recognition of all status changes
- **Emotional Connection**: Design respects that this monitors a living being
- **Theme Extensibility**: Easy to add new themes without breaking existing functionality
- **Visual Consistency**: Themes change colors/styles but maintain UX patterns

## Technical Requirements

### Backend Integration
- **API Base URL**: `http://10.0.20.69/api/`
- **Main Data Endpoint**: `/api/latest` (returns real-time sensor data)
- **Health Check**: `/api/health`
- **Weather API**: OpenWeatherMap API integration
- **Update Frequency**: Every 2 seconds for sensors, every 10 minutes for weather
- **Data Format**: JSON with basking area and cooling area temperature/humidity
- **Location**: Portland, Oregon (lat: 45.5152, lon: -122.6784) for weather data

### Frontend Technology Stack
- **Framework**: Vanilla HTML5, CSS3, JavaScript (no external dependencies for reliability)
- **Design**: Beautiful, professional interface with extensible theme system
- **Layout**: Full-screen pages with smooth transitions
- **Updates**: Real-time data fetching every 2 seconds with visual feedback
- **Animations**: Smooth, purposeful animations for status changes
- **Theme System**: Advanced CSS custom properties system with easy theme creation

## Advanced Theme System Architecture

### CSS Custom Properties Structure
```css
:root {
    /* Universal Layout Constants */
    --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --border-radius: 12px;
    --border-radius-large: 20px;
    --shadow-small: 0 2px 10px rgba(0, 0, 0, 0.1);
    --shadow-medium: 0 8px 25px rgba(0, 0, 0, 0.15);
    --shadow-large: 0 15px 35px rgba(0, 0, 0, 0.2);
    
    /* Universal Status Colors */
    --status-excellent: #10B981;
    --status-good: #22C55E;
    --status-warning: #F59E0B;
    --status-critical: #EF4444;
    --status-info: #3B82F6;
    --status-offline: #6B7280;
}

/* Theme Template Structure */
.theme-{THEME_NAME} {
    /* Backgrounds (Required) */
    --bg-primary: /* Main page background gradient */;
    --bg-secondary: /* Card backgrounds */;
    --bg-tertiary: /* Secondary card elements */;
    --bg-header: /* Animated header gradient */;
    --bg-card: /* Individual cards */;
    --bg-button: /* Button backgrounds */;
    --bg-button-hover: /* Button hover state */;
    --bg-navigation: /* Navigation bar */;
    
    /* Text Colors (Required) */
    --text-primary: /* Main text */;
    --text-secondary: /* Secondary text */;
    --text-tertiary: /* Tertiary/muted text */;
    --text-accent: /* Accent text */;
    --text-on-primary: /* Text on colored backgrounds */;
    
    /* Accents & Highlights (Required) */
    --accent-primary: /* Main accent color */;
    --accent-secondary: /* Secondary accent */;
    --accent-gradient: /* Accent gradient */;
    --highlight: /* Highlight backgrounds */;
    --overlay: /* Modal/overlay backgrounds */;
    
    /* Borders & Dividers (Required) */
    --border-light: /* Light borders */;
    --border-medium: /* Medium borders */;
    --divider: /* Divider lines */;
    
    /* Interactive States (Optional) */
    --hover-lift: translateY(-2px);
    --active-scale: scale(0.98);
}
```

### Built-in Themes to Include

#### 1. Professional Day (Default)
```css
.theme-professional-day {
    --bg-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --bg-secondary: rgba(255, 255, 255, 0.95);
    --bg-header: linear-gradient(135deg, #87CEEB 0%, #98D8E8 50%, #B6E5F0 100%);
    /* ... complete theme variables */
}
```

#### 2. Professional Night
```css
.theme-professional-night {
    --bg-primary: linear-gradient(135deg, #0c4a6e 0%, #1e3a8a 100%);
    --bg-secondary: rgba(15, 23, 42, 0.95);
    --bg-header: linear-gradient(135deg, #0c1445 0%, #1a237e 50%, #000051 100%);
    /* ... complete theme variables */
}
```

#### 3. Ocean Theme
```css
.theme-ocean {
    --bg-primary: linear-gradient(135deg, #006064 0%, #00838f 50%, #0097a7 100%);
    --text-primary: #004d40;
    --accent-primary: #00acc1;
    /* ... ocean-inspired colors */
}
```

#### 4. Forest Theme
```css
.theme-forest {
    --bg-primary: linear-gradient(135deg, #1b4332 0%, #2d5016 50%, #52734d 100%);
    --text-primary: #1b4332;
    --accent-primary: #74c69d;
    /* ... forest-inspired colors */
}
```

#### 5. Sunset Theme
```css
.theme-sunset {
    --bg-primary: linear-gradient(135deg, #c2410c 0%, #ea580c 50%, #fb923c 100%);
    --text-primary: #9a3412;
    --accent-primary: #f97316;
    /* ... sunset-inspired colors */
}
```

#### 6. High Contrast (Accessibility)
```css
.theme-high-contrast {
    --bg-primary: #000000;
    --bg-secondary: #ffffff;
    --text-primary: #000000;
    --text-on-primary: #ffffff;
    /* ... high contrast for accessibility */
}
```

## Page Structure (CRITICAL: NO SCROLLING)

### Page 1: Status Overview
```
CRITICAL: Must fit exactly in 100vh with no scrolling
Layout Requirements (Viewport Units):
┌─────────────────────────────────────┐ ← 100vw
│ 🌟 ANIMATED TURTLE HEADER (15vh) 🌙 │ ← Nyan-cat style turtle with
│    ✨ Stars + Real Moon Phase ✨    │   authentic rainbow trail & stars
│      🐢🌈✦✧⋆★☆ TurtX Monitor       │   + twinkling star field
├─────────────────┬───────────────────┤
│  🔥 BASKING     │   ❄️ COOL SIDE    │ ← 45vh
│  Temperature    │   Temperature     │
│    ##.#°F       │     ##.#°F        │
│  Humidity       │   Humidity        │
│    ##%          │     ##%           │
├─────────────────┴───────────────────┤
│   🌤️ Weather Card (10vh)            │ ← Portland, OR weather
│ 72°F • Partly Cloudy • 15 mph SW   │   with animated icons
├─────────────────────────────────────┤
│        System Indicators (20vh)     │ 
│ 🌡️Heater 💡UV ⚡Power 📡Net 🚨Alert│
├─────────────────────────────────────┤
│   Navigation Bar (20vh)             │ ← 100vh total
│      [STATUS] [CAMERA] [DATA]       │   + Theme Selector
└─────────────────────────────────────┘
```

### Animated Header Features (Nyan Cat Style)
- **Turtle Sprite**: Cute 🐢 with animated swimming motion
- **Authentic Rainbow Trail**: Horizontal color bands (red, orange, yellow, green, blue, purple, pink) flowing behind turtle
- **Trailing Stars**: Cute star characters (✦ ✧ ⋆ ★ ☆) that sparkle and flow with the rainbow
- **Star Field Background**: Twinkling stars across the header with parallax effect
- **Real Moon Phase**: Calculated lunar position and phase display
- **Theme Awareness**: Header colors adapt to current theme while maintaining animations

```css
.rainbow-trail {
    position: absolute;
    left: 80px;
    width: 200px;
    height: 40px;
    opacity: 0.9;
    overflow: hidden;
}

.rainbow-trail::before {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: 
        linear-gradient(90deg, 
            #ff0000 0%, #ff0000 14.28%,
            #ff7700 14.28%, #ff7700 28.56%,
            #ffdd00 28.56%, #ffdd00 42.84%,
            #00ff00 42.84%, #00ff00 57.12%,
            #0077ff 57.12%, #0077ff 71.4%,
            #4400ff 71.4%, #4400ff 85.68%,
            #ff0088 85.68%, #ff0088 100%
        );
    animation: rainbow-flow 3s linear infinite;
}

.rainbow-trail::after {
    content: '✦ ✧ ⋆ ★ ☆ ✦ ✧ ⋆ ★ ☆ ✦ ✧ ⋆ ★ ☆';
    position: absolute;
    top: -10px;
    left: 0;
    width: 300%;
    height: 60px;
    color: white;
    font-size: 16px;
    letter-spacing: 20px;
    text-shadow: 0 0 10px rgba(255,255,255,0.8);
    animation: stars-trail 2s linear infinite;
    z-index: 2;
    display: flex;
    align-items: center;
}

@keyframes rainbow-flow {
    0% { transform: translateX(0); }
    100% { transform: translateX(-200px); }
}

@keyframes stars-trail {
    0% { transform: translateX(0); }
    100% { transform: translateX(-300px); }
}
```

### Theme Selector Component
```html
<div class="theme-selector">
    <div class="theme-button theme-professional-day-btn active" data-theme="professional-day" title="Professional Day"></div>
    <div class="theme-button theme-professional-night-btn" data-theme="professional-night" title="Professional Night"></div>
    <div class="theme-button theme-ocean-btn" data-theme="ocean" title="Ocean"></div>
    <div class="theme-button theme-forest-btn" data-theme="forest" title="Forest"></div>
    <div class="theme-button theme-sunset-btn" data-theme="sunset" title="Sunset"></div>
    <div class="theme-button theme-high-contrast-btn" data-theme="high-contrast" title="High Contrast"></div>
</div>
```

## JavaScript Theme Management System

### ThemeManager Class
```javascript
class ThemeManager {
    constructor() {
        this.currentTheme = 'professional-day';
        this.autoThemeEnabled = true;
        this.themes = {
            'professional-day': 'Professional Day',
            'professional-night': 'Professional Night',
            'ocean': 'Ocean',
            'forest': 'Forest',
            'sunset': 'Sunset',
            'high-contrast': 'High Contrast'
        };
        this.init();
    }

    init() {
        this.loadStoredTheme();
        this.setupThemeButtons();
        this.setupAutoTheme();
    }

    switchTheme(themeName) {
        if (!this.themes[themeName]) return;

        // Remove current theme class
        document.body.className = document.body.className.replace(/theme-\S+/g, '');
        
        // Add new theme class
        document.body.classList.add(`theme-${themeName}`);
        
        // Update active button
        this.updateActiveButton(themeName);
        
        // Save preference
        localStorage.setItem('turtx-theme', themeName);
        
        // Update theme-dependent elements
        this.updateThemeElements();
        
        // Trigger custom event
        this.onThemeChange(themeName);
    }

    // Auto theme switching based on time
    setupAutoTheme() {
        setInterval(() => {
            if (this.autoThemeEnabled) {
                const hour = new Date().getHours();
                const shouldBeNight = hour < 6 || hour >= 20;
                const targetTheme = shouldBeNight ? 'professional-night' : 'professional-day';
                
                if (this.currentTheme !== targetTheme) {
                    this.switchTheme(targetTheme);
                }
            }
        }, 60000);
    }

    // Easy method to add new themes dynamically
    registerTheme(name, displayName, cssVariables) {
        this.themes[name] = displayName;
        
        // Inject CSS for new theme
        const style = document.createElement('style');
        let css = `.theme-${name} {\n`;
        for (const [property, value] of Object.entries(cssVariables)) {
            css += `    ${property}: ${value};\n`;
        }
        css += '}\n';
        style.textContent = css;
        document.head.appendChild(style);
        
        // Add theme button
        this.addThemeButton(name, displayName);
    }

    // Get current theme's CSS variables
    getThemeVariables() {
        const root = document.documentElement;
        const computedStyle = getComputedStyle(root);
        const vars = {};
        
        // Extract all custom properties
        for (const property of document.styleSheets[0].cssRules) {
            if (property.selectorText && property.selectorText.includes(`theme-${this.currentTheme}`)) {
                // Parse CSS variables from current theme
            }
        }
        
        return vars;
    }
}
```

## Key Features to Implement

### 1. Theme System Features
- **Easy Theme Creation**: Add new themes with just CSS custom properties
- **Theme Preview**: Hover effects on theme selector buttons
- **Theme Persistence**: Remember user's theme choice
- **Auto Theme Switching**: Day/night mode based on time
- **Theme Events**: Custom events when themes change
- **Accessibility**: High contrast theme for vision impairments
- **Theme API**: JavaScript methods to create/modify themes programmatically

### 2. Real-time Data Updates with Visual Feedback
- Fetch from `/api/latest` every 2 seconds with retry logic
- Subtle flash animation when data updates (theme-aware colors)
- Connection status indicator with theme-appropriate styling
- Temperature value counting animations with theme colors

### 3. Weather Integration System
- OpenWeatherMap API integration with Portland, OR location awareness
- Animated weather icons that respond to actual conditions and themes
- Minimal, clean weather display with temp, wind, humidity
- Theme-aware weather card styling
- Real-time updates every 10 minutes with smooth transitions

### 4. Smart Log Management & Alert System
- Theme-aware log filtering with color-coded severity levels
- Interactive expandable log entries with theme-appropriate styling
- Smart grouping and pattern detection
- Touch-friendly interface with theme-consistent animations

### 5. Professional Monitoring Features
- Critical monitoring system with theme-aware alert colors
- System health indicators that adapt to current theme
- Status mapping with universal color meanings across themes
- Graceful degradation with theme-consistent fallback states

## Development Tasks - THEME-AWARE IMPLEMENTATION

**STEP 0 - CLEANUP REQUIRED:**
- Delete all existing broken/messy HTML, CSS, and JS files
- Start completely fresh with clean, organized code structure

**STEP 1 - Theme System Foundation:**
1. Create CSS custom properties structure for all theme variables
2. Implement base ThemeManager class with theme switching logic
3. Create theme selector component with preview functionality
4. Add theme persistence and auto-switching capabilities

**STEP 2 - Core Dashboard with Theme Support:**
1. Create HTML structure with theme-aware classes
2. Implement viewport-exact sizing (100vh, no scrolling)
3. Build all 6 built-in themes with complete variable sets
4. Add smooth theme transition animations

**STEP 3 - Advanced Features:**
1. Implement authentic Nyan Cat style turtle trail with rainbow and stars
2. Add real-time data integration with theme-aware visual feedback
3. Create weather system with theme-appropriate styling
4. Build smart log system with theme-consistent colors

**STEP 4 - Polish & Testing:**
1. Test all themes across different screen sizes
2. Verify no scrolling on any theme/page combination
3. Ensure accessibility compliance for high contrast theme
4. Add theme preview and smooth transition effects

## File Structure
```
dashboard/
├── index.html          # Main HTML with theme selector
├── styles/
│   ├── base.css       # Base styles and layout
│   ├── themes.css     # All theme definitions
│   └── animations.css # Animations and effects
├── scripts/
│   ├── theme-manager.js    # Theme system
│   ├── dashboard.js       # Main dashboard logic
│   └── api-client.js      # API integration
└── assets/            # Icons, images (optional)
```

## Expected API Response Format
```javascript
{
  "timestamp": "2024-08-27T14:32:00Z",
  "basking_area": {
    "temperature": 95.2,
    "humidity": 45,
    "temperature_unit": "F"
  },
  "cooling_area": {
    "temperature": 78.5,
    "humidity": 65,
    "temperature_unit": "F"
  },
  "system_status": {
    "heater": "on",
    "uv_light": "on", 
    "power": "stable",
    "network": "connected",
    "alerts": "none"
  }
}
```

## Theme Creation Guide for Future Development

### Adding a New Theme (Example: "Midnight Blue")
```css
/* 1. Add theme CSS */
.theme-midnight-blue {
    --bg-primary: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    --bg-secondary: rgba(14, 21, 58, 0.95);
    --text-primary: #e0e6ed;
    --accent-primary: #4facfe;
    /* ... complete all required variables */
}

/* 2. Add theme button styling */
.theme-midnight-blue-btn { 
    background: linear-gradient(45deg, #1a1a2e, #16213e); 
}
```

```javascript
// 3. Register theme in JavaScript
themeManager.registerTheme('midnight-blue', 'Midnight Blue', {
    '--bg-primary': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    '--bg-secondary': 'rgba(14, 21, 58, 0.95)',
    // ... other variables
});
```

## Success Criteria
- **Visual Excellence**: Beautiful, professional interface worthy of a medical device
- **Theme Flexibility**: Easy to add new themes without breaking existing functionality
- **Zero Scrolling**: All content fits exactly within 100vh on all themes
- **Smooth Performance**: 60fps animations and transitions on all themes
- **Reliability**: Rock-solid monitoring system that never fails
- **Accessibility**: High contrast theme meets WCAG AA standards
- **Extensibility**: Clean code structure for easy future enhancements

Create a **stunning, theme-flexible dashboard** that combines the reliability needed for life-support monitoring with the visual appeal and customization options that make it a joy to use. The theme system should be so well-designed that adding new themes becomes trivial for future development.

**DESIGN GOALS:**
- Beautiful enough to be proud of (across all themes)
- Professional enough to trust a life with
- Flexible enough to match any aesthetic preference
- Smooth enough to feel premium on every theme switch
- Reliable enough to never fail when needed

The final result should make users say "wow" while providing the rock-solid reliability required for life-support monitoring, with the added delight of being able to customize the visual experience to their personal taste.