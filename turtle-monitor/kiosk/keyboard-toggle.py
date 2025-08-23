#!/usr/bin/env python3
import tkinter as tk
import subprocess
import os
import time

class KeyboardToggle:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⌨️")
        self.root.geometry("25x20+995+575")  # Very small button, bottom-right corner
        self.root.configure(bg="#4a7c59")  # Turtle green
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        # Create toggle button
        self.button = tk.Button(
            self.root,
            text="⌨️",
            font=("Arial", 7),
            bg="#4a7c59",
            fg="white",
            relief="flat",
            bd=0,
            command=self.toggle_keyboard
        )
        self.button.pack(fill="both", expand=True)
        
        self.keyboard_visible = False
        self.keyboard_window_id = None
        
    def toggle_keyboard(self):
        if self.keyboard_visible:
            self.hide_keyboard()
        else:
            self.show_keyboard()
    
    def show_keyboard(self):
        try:
            # Set environment
            env = os.environ.copy()
            env["DISPLAY"] = ":0"
            
            # Open the HTML virtual keyboard in a new Chrome window
            # Position it at the bottom of the screen
            keyboard_process = subprocess.Popen([
                "google-chrome-stable",
                "--new-window",
                "--window-position=0,300",
                "--window-size=1024,300",
                "--app=http://127.0.0.1:8123/local/keyboard/virtual-keyboard.html",
                "--disable-infobars",
                "--disable-notifications", 
                "--disable-extensions-except",
                "--disable-plugins",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--user-data-dir=/tmp/keyboard-chrome"
            ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait a moment for window creation
            time.sleep(2)
            
            # Try to find and manage the keyboard window
            try:
                result = subprocess.run([
                    "xdotool", "search", "--name", "Virtual Keyboard"
                ], capture_output=True, text=True, timeout=3)
                
                if result.stdout.strip():
                    self.keyboard_window_id = result.stdout.strip().split(n)[0]
                    
                    # Position the window at bottom of screen
                    subprocess.run([
                        "xdotool", "windowmove", self.keyboard_window_id, "0", "300"
                    ], timeout=2)
                    
                    # Make it always on top
                    subprocess.run([
                        "xdotool", "windowraise", self.keyboard_window_id
                    ], timeout=2)
                    
            except:
                pass
            
            self.keyboard_visible = True
            self.button.config(bg="#8b4513")  # Brown when active
            
        except Exception as e:
            self.keyboard_visible = False
    
    def hide_keyboard(self):
        try:
            if self.keyboard_window_id:
                # Close the specific keyboard window
                subprocess.run([
                    "xdotool", "windowclose", self.keyboard_window_id
                ], timeout=2)
                self.keyboard_window_id = None
            else:
                # Fallback: close any Virtual Keyboard windows
                subprocess.run([
                    "pkill", "-f", "virtual-keyboard.html"
                ], stderr=subprocess.DEVNULL)
            
            self.keyboard_visible = False
            self.button.config(bg="#4a7c59")  # Back to green
        except:
            self.keyboard_visible = False
            self.button.config(bg="#4a7c59")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KeyboardToggle()
    app.run()
