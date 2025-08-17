// Auto-login script for turtle kiosk
console.log("🐢 Turtle auto-login script loaded");

function autoLogin() {
    // Wait for the page to be ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", autoLogin);
        return;
    }
    
    console.log("🐢 Attempting auto-login...");
    
    // Look for username/password fields
    const usernameField = document.querySelector("input[type=\"text\"], input[name=\"username\"], ha-textfield[name=\"username\"] input");
    const passwordField = document.querySelector("input[type=\"password\"], input[name=\"password\"], ha-textfield[name=\"password\"] input");
    const loginButton = document.querySelector("button[type=\"submit\"], mwc-button[unelevated], paper-button");
    
    if (usernameField && passwordField) {
        console.log("🐢 Found login fields, filling credentials...");
        
        // Fill the fields
        usernameField.value = "shrimp";
        usernameField.dispatchEvent(new Event("input", { bubbles: true }));
        usernameField.dispatchEvent(new Event("change", { bubbles: true }));
        
        passwordField.value = "shrimp"; 
        passwordField.dispatchEvent(new Event("input", { bubbles: true }));
        passwordField.dispatchEvent(new Event("change", { bubbles: true }));
        
        // Submit the form after a short delay
        setTimeout(() => {
            if (loginButton) {
                console.log("🐢 Clicking login button...");
                loginButton.click();
            } else {
                // Try submitting the form directly
                const form = document.querySelector("form");
                if (form) {
                    console.log("🐢 Submitting form...");
                    form.submit();
                }
            }
        }, 500);
    } else {
        console.log("🐢 No login fields found, might already be logged in");
    }
}

// Start auto-login process
setTimeout(autoLogin, 1000);
