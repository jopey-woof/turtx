#!/usr/bin/env python3
"""
Arducam Camera Optimizer
Comprehensive camera settings management for Arducam cameras
"""

import subprocess
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CameraControl:
    """Represents a camera control setting"""
    name: str
    control_id: str
    control_type: str
    min_value: int
    max_value: int
    default_value: int
    current_value: int
    step: int = 1
    menu_options: Optional[List[str]] = None

@dataclass
class CameraProfile:
    """Represents a camera settings profile"""
    name: str
    description: str
    settings: Dict[str, int]
    ir_filter: Optional[bool] = None

class ArducamOptimizer:
    """Comprehensive Arducam camera optimizer"""
    
    def __init__(self, device_path: str = "/dev/video0"):
        self.device_path = device_path
        self.controls: Dict[str, CameraControl] = {}
        self.profiles: Dict[str, CameraProfile] = {}
        self._load_controls()
        self._create_default_profiles()
    
    def _load_controls(self) -> None:
        """Load all available camera controls"""
        try:
            result = subprocess.run(
                ['v4l2-ctl', '-d', self.device_path, '--list-ctrls'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to load camera controls: {result.stderr}")
                return
            
            # Join all lines and then split by control patterns
            full_output = result.stdout
            
            # Split by section headers
            sections = full_output.split('\n\n')
            
            for section in sections:
                if 'User Controls' in section:
                    self._parse_section(section, 'user')
                elif 'Camera Controls' in section:
                    self._parse_section(section, 'camera')
                elif 'Extended Controls' in section:
                    self._parse_section(section, 'extended')
                    
        except Exception as e:
            logger.error(f"Error loading camera controls: {e}")
    
    def _parse_section(self, section: str, section_type: str) -> None:
        """Parse a section of controls"""
        try:
            # Split by lines and look for control patterns
            lines = section.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or 'Controls' in line:
                    continue
                
                # Look for lines that contain hex IDs and control information
                if '0x' in line and '(' in line and ')' in line:
                    # This might be a control line, but it could be split
                    # Let's reconstruct the full control line
                    control_line = self._reconstruct_control_line(lines, line)
                    if control_line:
                        self._parse_control_line(control_line, section_type)
                        
        except Exception as e:
            logger.error(f"Error parsing section: {e}")
    
    def _reconstruct_control_line(self, lines: list, start_line: str) -> str:
        """Reconstruct a complete control line from potentially split lines"""
        try:
            # Find the line index
            line_index = -1
            for i, line in enumerate(lines):
                if start_line in line:
                    line_index = i
                    break
            
            if line_index == -1:
                return None
            
            # Start with the current line
            control_line = start_line
            
            # Look ahead for continuation lines
            i = line_index + 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                
                # If the next line starts with ':', it's a continuation
                if next_line.startswith(':'):
                    control_line += next_line
                    i += 1
                # If it contains control values (min=, max=, etc.), it's a continuation
                elif any(keyword in next_line for keyword in ['min=', 'max=', 'default=', 'value=']):
                    control_line += ' ' + next_line
                    i += 1
                else:
                    break
            
            return control_line
            
        except Exception as e:
            logger.error(f"Error reconstructing control line: {e}")
            return None
    
    def _parse_control_line(self, line: str, section: str) -> None:
        """Parse a control line from v4l2-ctl output"""
        try:
            # Split by the first colon to separate name/type from values
            parts = line.split(':', 1)
            if len(parts) < 2:
                return
                
            name_type_part = parts[0].strip()
            values_part = parts[1].strip()
            
            # Extract control name and type
            # Format: "brightness 0x00980900 (int)"
            if '(' in name_type_part and ')' in name_type_part:
                # Find the last space before the hex ID
                name_hex_part = name_type_part.split('(')[0].strip()
                # Find the last space to separate name from hex ID
                last_space = name_hex_part.rfind(' ')
                if last_space > 0:
                    name = name_hex_part[:last_space].strip()
                else:
                    name = name_hex_part
                
                # Extract control type
                control_type = name_type_part.split('(')[1].split(')')[0]
                
                # Create control ID from name
                control_id = name.lower().replace(' ', '_')
            else:
                return  # Skip malformed lines
            
            # Parse values part
            # Format: "min=-64 max=64 step=1 default=0 value=25"
            min_val = 0
            max_val = 0
            step_val = 1
            default_val = 0
            current_val = 0
            menu_options = None
            
            if 'min=' in values_part and 'max=' in values_part:
                # Extract numeric values
                try:
                    min_val = int(values_part.split('min=')[1].split()[0])
                    max_val = int(values_part.split('max=')[1].split()[0])
                    if 'step=' in values_part:
                        step_val = int(values_part.split('step=')[1].split()[0])
                    if 'default=' in values_part:
                        default_val = int(values_part.split('default=')[1].split()[0])
                    if 'value=' in values_part:
                        current_val = int(values_part.split('value=')[1].split()[0])
                except (ValueError, IndexError):
                    logger.warning(f"Failed to parse numeric values from: {values_part}")
            else:
                # Handle menu controls
                if '(' in values_part:
                    # Extract menu options
                    menu_options = []
                    for option in values_part.split('('):
                        if ')' in option:
                            menu_options.append(option.split(')')[0].strip())
                    if menu_options:
                        max_val = len(menu_options) - 1
            
            # Create the control object
            self.controls[control_id] = CameraControl(
                name=name,
                control_id=control_id,
                control_type=control_type,
                min_value=min_val,
                max_value=max_val,
                default_value=default_val,
                current_value=current_val,
                step=step_val,
                menu_options=menu_options
            )
            
        except Exception as e:
            logger.error(f"Error parsing control line '{line}': {e}")
    
    def _create_default_profiles(self) -> None:
        """Create default camera profiles"""
        
        # Daylight profile
        self.profiles["daylight"] = CameraProfile(
            name="Daylight",
            description="Optimized for bright daylight conditions",
            settings={
                "brightness": 0,
                "contrast": 32,
                "saturation": 64,
                "white_balance_temperature": 5500,
                "exposure_time_absolute": 100,
                "gain": 5,
                "sharpness": 3
            }
        )
        
        # Low light profile
        self.profiles["low_light"] = CameraProfile(
            name="Low Light",
            description="Optimized for low light conditions",
            settings={
                "brightness": 10,
                "contrast": 40,
                "saturation": 70,
                "white_balance_temperature": 4000,
                "exposure_time_absolute": 200,
                "gain": 20,
                "sharpness": 2
            }
        )
        
        # Night vision profile (potential IR)
        self.profiles["night_vision"] = CameraProfile(
            name="Night Vision",
            description="Optimized for night vision/IR conditions",
            settings={
                "brightness": 15,
                "contrast": 50,
                "saturation": 30,
                "white_balance_temperature": 3000,
                "exposure_time_absolute": 500,
                "gain": 30,
                "sharpness": 1
            },
            ir_filter=False
        )
        
        # Turtle monitoring profile
        self.profiles["turtle_monitor"] = CameraProfile(
            name="Turtle Monitor",
            description="Optimized for turtle habitat monitoring",
            settings={
                "brightness": 5,
                "contrast": 35,
                "saturation": 75,
                "white_balance_temperature": 4800,
                "exposure_time_absolute": 150,
                "gain": 12,
                "sharpness": 4
            }
        )
    
    def get_control_value(self, control_id: str) -> Optional[int]:
        """Get current value of a control"""
        if control_id in self.controls:
            return self.controls[control_id].current_value
        return None
    
    def set_control_value(self, control_id: str, value: int) -> bool:
        """Set value of a control"""
        try:
            if control_id not in self.controls:
                logger.error(f"Control {control_id} not found")
                return False
            
            control = self.controls[control_id]
            if value < control.min_value or value > control.max_value:
                logger.error(f"Value {value} out of range for {control_id}")
                return False
            
            result = subprocess.run(
                ['v4l2-ctl', '-d', self.device_path, f'--set-ctrl={control_id}={value}'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                control.current_value = value
                logger.info(f"Set {control_id} to {value}")
                return True
            else:
                logger.error(f"Failed to set {control_id}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting control {control_id}: {e}")
            return False
    
    def apply_profile(self, profile_name: str) -> bool:
        """Apply a camera profile"""
        if profile_name not in self.profiles:
            logger.error(f"Profile {profile_name} not found")
            return False
        
        profile = self.profiles[profile_name]
        success = True
        
        for control_id, value in profile.settings.items():
            if not self.set_control_value(control_id, value):
                success = False
        
        if success:
            logger.info(f"Applied profile: {profile_name}")
        
        return success
    
    def detect_ir_filter(self) -> Optional[bool]:
        """Detect if IR filter is present and controllable"""
        # Check for common IR filter control names
        ir_controls = [
            'ir_filter', 'ir_cut_filter', 'night_mode', 'ir_led',
            'ir_illuminator', 'ir_light', 'night_vision'
        ]
        
        for control_id in ir_controls:
            if control_id in self.controls:
                logger.info(f"Found IR-related control: {control_id}")
                return self.get_control_value(control_id) == 1
        
        # Check for extended controls that might be IR-related
        try:
            result = subprocess.run(
                ['v4l2-ctl', '-d', self.device_path, '--all'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                if 'ir' in output or 'night' in output or 'filter' in output:
                    logger.info("Found potential IR-related controls in extended output")
                    return None  # Indicates potential but not confirmed
        
        except Exception as e:
            logger.error(f"Error detecting IR filter: {e}")
        
        return None
    
    def optimize_for_conditions(self, brightness_level: str = "auto") -> bool:
        """Automatically optimize camera for current conditions"""
        try:
            # Get current exposure and gain to estimate lighting
            exposure = self.get_control_value("exposure_time_absolute")
            gain = self.get_control_value("gain")
            
            if exposure and gain:
                # Determine lighting conditions
                if exposure > 300 or gain > 20:
                    # Low light conditions
                    return self.apply_profile("low_light")
                elif exposure < 100 and gain < 10:
                    # Bright conditions
                    return self.apply_profile("daylight")
                else:
                    # Medium conditions
                    return self.apply_profile("turtle_monitor")
            
            # Default to turtle monitor profile
            return self.apply_profile("turtle_monitor")
            
        except Exception as e:
            logger.error(f"Error optimizing for conditions: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get comprehensive camera status"""
        return {
            "device": self.device_path,
            "controls": {
                control_id: {
                    "name": control.name,
                    "current_value": control.current_value,
                    "range": f"{control.min_value}-{control.max_value}",
                    "type": control.control_type
                }
                for control_id, control in self.controls.items()
            },
            "profiles": {
                name: {
                    "description": profile.description,
                    "settings": profile.settings
                }
                for name, profile in self.profiles.items()
            },
            "ir_filter": self.detect_ir_filter(),
            "optimization_available": len(self.controls) > 0
        }
    
    def create_custom_profile(self, name: str, description: str, settings: Dict[str, int]) -> bool:
        """Create a custom camera profile"""
        try:
            # Validate settings
            for control_id, value in settings.items():
                if control_id not in self.controls:
                    logger.error(f"Control {control_id} not found")
                    return False
                
                control = self.controls[control_id]
                if value < control.min_value or value > control.max_value:
                    logger.error(f"Value {value} out of range for {control_id}")
                    return False
            
            self.profiles[name] = CameraProfile(
                name=name,
                description=description,
                settings=settings
            )
            
            logger.info(f"Created custom profile: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom profile: {e}")
            return False

# Global optimizer instance
camera_optimizer = ArducamOptimizer() 