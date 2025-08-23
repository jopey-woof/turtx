// Turtle Kiosk Auto-Login Script
console.log('🐢 Turtle kiosk auto-login script loaded');

// Configuration
const CONFIG = {
    username: 'shrimp',
    password: 'shrimp',
    dashboardUrl: '/lovelace-kiosk',
    maxRetries: 3,
    retryDelay: 2000,
    loginTimeout: 10000
};

let retryCount = 0;

function showStatus(message) {
    console.log('🐢 Status:', message);
    
    // Create or update status element
    let statusEl = document.getElementById('turtle-status');
    if (!statusEl) {
        statusEl = document.createElement('div');
        statusEl.id = 'turtle-status';
        statusEl.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-family: Arial, sans-serif;
            font-size: 12px;
            z-index: 9999;
        `;
        document.body.appendChild(statusEl);
    }
    statusEl.textContent = `🐢 ${message}`;
}

function checkIfLoggedIn() {
    // Check if we're already logged in by looking for HA elements
    const haElements = document.querySelectorAll('home-assistant, ha-app-layout, ha-sidebar');
    if (haElements.length > 0) {
        console.log('🐢 Already logged in, redirecting to dashboard...');
        showStatus('Already logged in, redirecting...');
        setTimeout(() => {
            window.location.href = CONFIG.dashboardUrl;
        }, 1000);
        return true;
    }
    return false;
}

function attemptLogin() {
    showStatus(`Login attempt ${retryCount + 1}/${CONFIG.maxRetries}`);
    
    // Look for login form elements
    const usernameField = document.querySelector('input[name="username"], input[type="text"], ha-textfield[name="username"] input');
    const passwordField = document.querySelector('input[name="password"], input[type="password"], ha-textfield[name="password"] input');
    const loginButton = document.querySelector('button[type="submit"], mwc-button[unelevated], paper-button, ha-button');
    
    if (usernameField && passwordField) {
        console.log('🐢 Found login fields, filling credentials...');
        showStatus('Filling login form...');
        
        // Fill username
        usernameField.value = CONFIG.username;
        usernameField.dispatchEvent(new Event('input', { bubbles: true }));
        usernameField.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Fill password
        passwordField.value = CONFIG.password;
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
        console.log('🐢 Login fields not found, might be on different page');
        showStatus('Login fields not found');
        
        // Check if we're on a different page that might need navigation
        if (window.location.pathname.includes('/auth/')) {
            // We're on an auth page, try to navigate to login flow
            window.location.href = '/auth/login_flow';
        } else if (retryCount < CONFIG.maxRetries) {
            retryCount++;
            setTimeout(attemptLogin, CONFIG.retryDelay);
        } else {
            showStatus('Login failed after max retries');
        }
    }
}

function checkLoginSuccess() {
    // Check if login was successful
    if (checkIfLoggedIn()) {
        return;
    }
    
    // Check for error messages
    const errorElements = document.querySelectorAll('.error, .alert, [role="alert"]');
    if (errorElements.length > 0) {
        const errorText = errorElements[0].textContent;
        console.log('🐢 Login error detected:', errorText);
        showStatus(`Login error: ${errorText.substring(0, 30)}...`);
    }
    
    // Retry if we haven't exceeded max retries
    if (retryCount < CONFIG.maxRetries) {
        retryCount++;
        console.log(`🐢 Retrying login (${retryCount}/${CONFIG.maxRetries})...`);
        setTimeout(attemptLogin, CONFIG.retryDelay);
    } else {
        showStatus('Login failed - check credentials');
    }
}

function startAutoLogin() {
    console.log('🐢 Starting auto-login process...');
    showStatus('Starting auto-login...');
    
    // Wait for page to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startAutoLogin);
        return;
    }
    
    // Check if already logged in
    if (checkIfLoggedIn()) {
        return;
    }
    
    // Start login process
    setTimeout(attemptLogin, 1000);
}

// Start the auto-login process
startAutoLogin();

// Also listen for navigation changes
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        console.log('🐢 URL changed to:', url);
        
        // If we're on the dashboard, we're done
        if (url.includes('/lovelace-kiosk')) {
            showStatus('Dashboard loaded successfully!');
            setTimeout(() => {
                const statusEl = document.getElementById('turtle-status');
                if (statusEl) {
                    statusEl.style.display = 'none';
                }
            }, 3000);
        }
    }
}).observe(document, { subtree: true, childList: true }); 