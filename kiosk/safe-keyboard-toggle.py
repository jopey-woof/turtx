#!/usr/bin/env python3
"""
Safe Keyboard Toggle for Turtle Kiosk
This version avoids any window management commands that could interfere with sensor data input
"""
import tkinter as tk
import subprocess
import os
import time
import signal

class SafeKeyboardToggle:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⌨️")
        self.root.geometry("30x25+990+570")  # Slightly larger for easier touch
        self.root.configure(bg="#4a7c59")  # Turtle green
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # No window decorations
        
        # Make window click-through when keyboard is hidden
        self.root.attributes("-alpha", 0.8)
        
        # Create toggle button
        self.button = tk.Button(
            self.root,
            text="⌨️",
            font=("Arial", 10),
            bg="#4a7c59",
            fg="white",
            relief="flat",
            bd=0,
            command=self.toggle_keyboard
        )
        self.button.pack(fill="both", expand=True)
        
        self.keyboard_visible = False
        self.keyboard_process = None
        
    def toggle_keyboard(self):
        if self.keyboard_visible:
            self.hide_keyboard()
        else:
            self.show_keyboard()
    
    def show_keyboard(self):
        try:
            # Kill any existing keyboard processes
            self.hide_keyboard()
            time.sleep(0.5)
            
            # Start onboard with minimal interference
            env = os.environ.copy()
            env["DISPLAY"] = ":0"
            
            # Use a more conservative approach - just start the keyboard
            # Let the window manager handle positioning naturally
            self.keyboard_process = subprocess.Popen([
                "onboard", 
                "--layout=Compact", 
                "--theme=Nightshade", 
                "--size=600x200"
            ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.keyboard_visible = True
            self.button.config(bg="#8b4513")  # Brown when active
            self.root.attributes("-alpha", 1.0)  # Fully visible when active
            
        except Exception as e:
            print(f"Keyboard show error: {e}")
    
    def hide_keyboard(self):
        try:
            # Kill onboard processes
            subprocess.run(["pkill", "-f", "onboard"], stderr=subprocess.DEVNULL)
            
            # Also kill our specific process if it exists
            if self.keyboard_process:
                try:
                    self.keyboard_process.terminate()
                    self.keyboard_process.wait(timeout=2)
                except:
                    try:
                        self.keyboard_process.kill()
                    except:
                        pass
                self.keyboard_process = None
            
            self.keyboard_visible = False
            self.button.config(bg="#4a7c59")  # Back to green
            self.root.attributes("-alpha", 0.8)  # Semi-transparent when hidden
            
        except Exception as e:
            print(f"Keyboard hide error: {e}")
    
    def on_closing(self):
        """Clean shutdown"""
        self.hide_keyboard()
        self.root.destroy()
    
    def run(self):
        # Set up clean shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Handle Ctrl+C gracefully
        def signal_handler(signum, frame):
            self.on_closing()
        
        signal.signal(signal.SIGINT, signal_handler)
        
        self.root.mainloop()

if __name__ == "__main__":
    app = SafeKeyboardToggle()
    app.run() 