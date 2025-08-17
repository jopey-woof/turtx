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
        self.root.overrideredirect(True)  # No window decorations
        
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
        
    def toggle_keyboard(self):
        if self.keyboard_visible:
            self.hide_keyboard()
        else:
            self.show_keyboard()
    
    def show_keyboard(self):
        try:
            # Kill any existing keyboard
            subprocess.run(["pkill", "-f", "onboard"], stderr=subprocess.DEVNULL)
            time.sleep(0.3)
            
            # Start onboard at bottom left with proper z-order
            env = os.environ.copy()
            env["DISPLAY"] = ":0"
            
            # Start keyboard
            subprocess.Popen([
                "onboard", 
                "--layout=Compact", 
                "--theme=Nightshade", 
                "--size=600x200"
            ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            time.sleep(2)
            
            # Position at bottom left and force to front
            subprocess.run(["wmctrl", "-r", "Onboard", "-e", "0,10,400,600,200"], 
                         stderr=subprocess.DEVNULL, timeout=2)
            time.sleep(0.2)
            subprocess.run(["wmctrl", "-r", "Onboard", "-b", "add,above"], 
                         stderr=subprocess.DEVNULL, timeout=2)
            time.sleep(0.2)
            subprocess.run(["wmctrl", "-r", "Onboard", "-a"], 
                         stderr=subprocess.DEVNULL, timeout=2)
            
            self.keyboard_visible = True
            self.button.config(bg="#8b4513")  # Brown when active
            
        except:
            pass
    
    def hide_keyboard(self):
        try:
            subprocess.run(["pkill", "-f", "onboard"], stderr=subprocess.DEVNULL)
            self.keyboard_visible = False
            self.button.config(bg="#4a7c59")  # Back to green
        except:
            pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = KeyboardToggle()
    app.run()