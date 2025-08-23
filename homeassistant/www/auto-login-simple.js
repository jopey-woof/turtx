// Simple Auto-Login Script for Turtle Kiosk
console.log('🐢 Turtle auto-login script loaded');

// Configuration
const USERNAME = 'shrimp';
const PASSWORD = 'shrimp';
const DASHBOARD_URL = '/lovelace-kiosk';

let loginAttempts = 0;
const MAX_ATTEMPTS = 5;

function showStatus(message) {
    console.log('🐢 Status:', message);
    
    // Create status indicator
    let statusEl = document.getElementById('turtle-login-status');
    if (!statusEl) {
        statusEl = document.createElement('div');
        statusEl.id = 'turtle-login-status';
        statusEl.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-family: Arial, sans-serif;
            font-size: 11px;
            z-index: 9999;
            pointer-events: none;
        `;
        document.body.appendChild(statusEl);
    }
    statusEl.textContent = `🐢 ${message}`;
}

function attemptLogin() {
    loginAttempts++;
    showStatus(`Login attempt ${loginAttempts}/${MAX_ATTEMPTS}`);
    
    // Look for login form elements
    const usernameField = document.querySelector('input[name="username"], input[type="text"], ha-textfield[name="username"] input, paper-input[name="username"] input');
    const passwordField = document.querySelector('input[name="password"], input[type="password"], ha-textfield[name="password"] input, paper-input[name="password"] input');
    const loginButton = document.querySelector('button[type="submit"], mwc-button[unelevated], paper-button, ha-button, input[type="submit"]');
    
    if (usernameField && passwordField) {
        console.log('🐢 Found login fields, filling credentials...');
        showStatus('Filling login form...');
        
        // Fill username
        usernameField.value = USERNAME;
        usernameField.dispatchEvent(new Event('input', { bubbles: true }));
        usernameField.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Fill password
        passwordField.value = PASSWORD;
        passwordField.dispatchEvent(new Event('input', { bubbles: true }));
        passwordField.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Submit form
        setTimeout(() => {
            if (loginButton) {
                console.log('🐢 Clicking login button...');
                showStatus('Submitting login...');
                loginButton.click();
            } else {
                // Try to find and submit the form
                const form = document.querySelector('form');
                if (form) {
                    console.log('🐢 Submitting form...');
                    showStatus('Submitting form...');
                    form.submit();
                }
            }
        }, 500);
        
        // Check for successful login after a delay
        setTimeout(checkLoginSuccess, 3000);
        
    } else {
        console.log('🐢 Login fields not found');
        showStatus('Login fields not found');
        
        // Check if we're already logged in
        if (document.querySelector('home-assistant, ha-app-layout, ha-sidebar')) {
            console.log('🐢 Already logged in, redirecting to dashboard...');
            showStatus('Already logged in, redirecting...');
            setTimeout(() => {
                window.location.href = DASHBOARD_URL;
            }, 1000);
            return;
        }
        
        // Retry if we haven't exceeded max attempts
        if (loginAttempts < MAX_ATTEMPTS) {
            setTimeout(attemptLogin, 2000);
        } else {
            showStatus('Login failed - max attempts reached');
        }
    }
}

function checkLoginSuccess() {
    // Check if login was successful
    if (document.querySelector('home-assistant, ha-app-layout, ha-sidebar')) {
        console.log('🐢 Login successful, redirecting to dashboard...');
        showStatus('Login successful!');
        setTimeout(() => {
            window.location.href = DASHBOARD_URL;
        }, 1000);
        return;
    }
    
    // Check for error messages
    const errorElements = document.querySelectorAll('.error, .alert, [role="alert"], .invalid');
    if (errorElements.length > 0) {
        const errorText = errorElements[0].textContent;
        console.log('🐢 Login error detected:', errorText);
        showStatus(`Login error: ${errorText.substring(0, 30)}...`);
    }
    
    // Retry if we haven't exceeded max attempts
    if (loginAttempts < MAX_ATTEMPTS) {
        console.log(`🐢 Retrying login (${loginAttempts}/${MAX_ATTEMPTS})...`);
        setTimeout(attemptLogin, 2000);
    } else {
        showStatus('Login failed - check credentials');
    }
}

// Start the auto-login process
console.log('🐢 Starting auto-login process...');
showStatus('Starting auto-login...');

// Wait for page to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(attemptLogin, 1000);
    });
} else {
    setTimeout(attemptLogin, 1000);
} 