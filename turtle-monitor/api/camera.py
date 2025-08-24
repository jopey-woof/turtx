#!/usr/bin/env python3
"""
🐢 Turtle Monitor Camera Management
OpenCV-based camera management for Arducam 1080P USB camera
"""

import os
import cv2
import time
import logging
import threading
import numpy as np
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class CameraManager:
    """Camera management class for Arducam USB camera"""
    
    def __init__(self):
        self.camera = None
        self.camera_index = 0
        self.is_connected = False
        self.last_frame = None
        self.last_frame_time = None
        self.frame_width = 1920
        self.frame_height = 1080
        self.fps = 30  # Increased to 30 FPS for better quality
        self.quality = 85  # JPEG quality
        self.ir_mode = False
        self.auto_ir = True
        self.health_check_interval = 60  # seconds
        self.max_recovery_time = 60  # seconds
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        
        # Camera settings
        self.camera_settings = {
            'brightness': 25,  # Optimized for less washed out appearance
            'contrast': 65,    # Increased for better definition
            'saturation': 55,  # Slightly increased for better colors
            'hue': 0,
            'gain': 15,        # Reduced to minimize noise and brightness
            'auto_exposure': 1,  # Manual exposure mode
            'exposure_time': 156,  # Optimized exposure time
            'sharpness': 3,    # Default sharpness
            'white_balance_auto': 1,  # Auto white balance
        }
        
        # Health monitoring
        self.health_data = {
            'last_check': None,
            'connection_status': 'disconnected',
            'frame_count': 0,
            'error_count': 0,
            'last_error': None,
            'uptime': 0,
            'fps_actual': 0,
            'resolution': f"{self.frame_width}x{self.frame_height}",
            'ir_mode': False,
            'auto_ir_enabled': self.auto_ir
        }
        
        # Threading
        self.lock = threading.Lock()
        self.health_thread = None
        self.should_stop = False
        
        # Initialize camera
        self.init_camera()
        self.start_health_monitoring()
    
    def init_camera(self) -> bool:
        """Initialize camera connection"""
        try:
            logger.info(f"🎥 Initializing camera at index {self.camera_index}")
            
            # Try to find camera device
            camera_device = self.find_camera_device()
            if camera_device:
                logger.info(f"Found camera device: {camera_device}")
            
            # Initialize OpenCV camera
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera at index {self.camera_index}")
                return False
            
            # Set camera properties
            self.set_camera_properties()
            
            # Test camera by capturing a frame
            ret, frame = self.camera.read()
            if not ret or frame is None:
                logger.error("Failed to capture test frame from camera")
                self.camera.release()
                return False
            
            self.is_connected = True
            self.last_frame = frame
            self.last_frame_time = time.time()
            self.health_data['connection_status'] = 'connected'
            self.health_data['last_check'] = datetime.now()
            self.recovery_attempts = 0
            
            logger.info("✅ Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            self.health_data['last_error'] = str(e)
            self.health_data['error_count'] += 1
            return False
    
    def find_camera_device(self) -> Optional[str]:
        """Find camera device path"""
        try:
            # Check common camera device paths
            camera_paths = [
                "/dev/video0",
                "/dev/video1", 
                "/dev/video2",
                "/dev/video3"
            ]
            
            for path in camera_paths:
                if os.path.exists(path):
                    logger.info(f"Found camera device: {path}")
                    return path
            
            # If no device found, try to list video devices
            import subprocess
            try:
                result = subprocess.run(['v4l2-ctl', '--list-devices'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Available video devices:\n{result.stdout}")
            except FileNotFoundError:
                logger.warning("v4l2-ctl not available for device listing")
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding camera device: {e}")
            return None
    
    def set_camera_properties(self):
        """Set camera properties for optimal turtle monitoring"""
        try:
            if not self.camera or not self.camera.isOpened():
                return
            
            # Set resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Set camera settings
            for setting, value in self.camera_settings.items():
                try:
                    if setting == 'brightness':
                        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, value)
                    elif setting == 'contrast':
                        self.camera.set(cv2.CAP_PROP_CONTRAST, value)
                    elif setting == 'saturation':
                        self.camera.set(cv2.CAP_PROP_SATURATION, value)
                    elif setting == 'hue':
                        self.camera.set(cv2.CAP_PROP_HUE, value)
                    elif setting == 'gain':
                        self.camera.set(cv2.CAP_PROP_GAIN, value)
                    elif setting == 'auto_exposure':
                        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, value)
                    elif setting == 'exposure_time':
                        self.camera.set(cv2.CAP_PROP_EXPOSURE, value)
                    elif setting == 'sharpness':
                        # Sharpness control not directly available in OpenCV
                        pass
                    elif setting == 'white_balance_auto':
                        self.camera.set(cv2.CAP_PROP_AUTO_WB, value)
                except Exception as e:
                    logger.warning(f"Failed to set {setting}: {e}")
            
            logger.info("Camera properties configured")
            
        except Exception as e:
            logger.error(f"Error setting camera properties: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame from camera"""
        try:
            with self.lock:
                if not self.camera or not self.camera.isOpened():
                    return None
                
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    logger.warning("Failed to capture frame")
                    return None
                
                # Update frame data
                self.last_frame = frame
                self.last_frame_time = time.time()
                self.health_data['frame_count'] += 1
                
                # Auto IR mode detection
                if self.auto_ir:
                    self.detect_ir_mode(frame)
                
                return frame
                
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
            self.health_data['last_error'] = str(e)
            self.health_data['error_count'] += 1
            return None
    
    def detect_ir_mode(self, frame: np.ndarray):
        """Detect if camera is in IR mode based on frame characteristics"""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate average brightness
            avg_brightness = np.mean(gray)
            
            # Calculate color distribution
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1])
            
            # IR mode typically has lower saturation and different brightness patterns
            was_ir = self.ir_mode
            self.ir_mode = (avg_brightness < 80 and saturation < 30)
            
            if was_ir != self.ir_mode:
                logger.info(f"IR mode {'enabled' if self.ir_mode else 'disabled'}")
                self.health_data['ir_mode'] = self.ir_mode
            
        except Exception as e:
            logger.warning(f"Error detecting IR mode: {e}")
    
    def get_snapshot(self) -> Optional[bytes]:
        """Get camera snapshot as JPEG bytes"""
        try:
            frame = self.get_frame()
            if frame is None:
                return None
            
            # Encode as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
            ret, jpeg_data = cv2.imencode('.jpg', frame, encode_param)
            
            if not ret:
                logger.error("Failed to encode JPEG")
                return None
            
            return jpeg_data.tobytes()
            
        except Exception as e:
            logger.error(f"Error getting snapshot: {e}")
            return None
    
    def get_stream_frame(self) -> Optional[bytes]:
        """Get frame for MJPEG streaming"""
        try:
            frame = self.get_frame()
            if frame is None:
                return None
            
            # Resize for streaming if needed
            if frame.shape[1] > 1280:  # Resize if width > 1280
                scale = 1280 / frame.shape[1]
                new_width = int(frame.shape[1] * scale)
                new_height = int(frame.shape[0] * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Encode as JPEG for streaming
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # Lower quality for streaming
            ret, jpeg_data = cv2.imencode('.jpg', frame, encode_param)
            
            if not ret:
                logger.error("Failed to encode stream frame")
                return None
            
            return jpeg_data.tobytes()
            
        except Exception as e:
            logger.error(f"Error getting stream frame: {e}")
            return None
    
    def check_health(self) -> Dict[str, Any]:
        """Check camera health and return status"""
        try:
            current_time = time.time()
            
            # Update uptime
            if self.health_data['last_check']:
                self.health_data['uptime'] = current_time - self.health_data['last_check'].timestamp()
            
            # Check if camera is still connected
            if self.camera and bool(self.camera.isOpened()):
                # Test frame capture
                ret, frame = self.camera.read()
                if bool(ret) and frame is not None:
                    self.health_data['connection_status'] = 'connected'
                    self.health_data['last_check'] = datetime.now()
                    
                    # Calculate actual FPS
                    if self.last_frame_time:
                        time_diff = current_time - self.last_frame_time
                        if time_diff > 0:
                            self.health_data['fps_actual'] = float(1.0 / time_diff)
                else:
                    self.health_data['connection_status'] = 'error'
                    logger.warning("Camera health check failed - no frame captured")
            else:
                self.health_data['connection_status'] = 'disconnected'
                logger.warning("Camera health check failed - camera not opened")
            
            # Convert numpy types to Python native types
            health_copy = self.health_data.copy()
            for key, value in health_copy.items():
                if hasattr(value, 'item'):  # numpy scalar
                    health_copy[key] = value.item()
                elif isinstance(value, bool):
                    health_copy[key] = bool(value)
                elif isinstance(value, (int, float)):
                    health_copy[key] = type(value)(value)
            
            return health_copy
            
        except Exception as e:
            logger.error(f"Error checking camera health: {e}")
            self.health_data['connection_status'] = 'error'
            self.health_data['last_error'] = str(e)
            return self.health_data.copy()
    
    def restart_camera(self) -> bool:
        """Restart camera connection"""
        try:
            logger.info("🔄 Restarting camera...")
            
            # Stop current camera
            if self.camera:
                self.camera.release()
                self.camera = None
            
            self.is_connected = False
            self.health_data['connection_status'] = 'restarting'
            
            # Wait a moment
            time.sleep(2)
            
            # Reinitialize
            success = self.init_camera()
            
            if success:
                logger.info("✅ Camera restart successful")
                self.recovery_attempts = 0
            else:
                logger.error("❌ Camera restart failed")
                self.recovery_attempts += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Error restarting camera: {e}")
            self.recovery_attempts += 1
            return False
    
    def start_health_monitoring(self):
        """Start background health monitoring thread"""
        if self.health_thread and self.health_thread.is_alive():
            return
        
        self.should_stop = False
        self.health_thread = threading.Thread(target=self._health_monitor_loop, daemon=True)
        self.health_thread.start()
        logger.info("Started camera health monitoring")
    
    def _health_monitor_loop(self):
        """Health monitoring loop"""
        while not self.should_stop:
            try:
                # Check health
                health = self.check_health()
                
                # Auto-recovery logic
                if (health['connection_status'] in ['disconnected', 'error'] and 
                    self.recovery_attempts < self.max_recovery_attempts):
                    
                    logger.warning(f"Camera health check failed, attempting recovery (attempt {self.recovery_attempts + 1})")
                    self.restart_camera()
                
                # Sleep for health check interval
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(10)  # Shorter sleep on error
    
    def stop(self):
        """Stop camera and cleanup"""
        try:
            logger.info("🛑 Stopping camera manager...")
            
            self.should_stop = True
            
            if self.health_thread and self.health_thread.is_alive():
                self.health_thread.join(timeout=5)
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            self.is_connected = False
            logger.info("Camera manager stopped")
            
        except Exception as e:
            logger.error(f"Error stopping camera manager: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive camera status"""
        health = self.check_health()
        
        # Convert numpy types to Python native types for JSON serialization
        def convert_numpy_types(obj):
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(v) for v in obj]
            else:
                return obj
        
        status = {
            "connected": bool(self.is_connected),
            "device": f"/dev/video{self.camera_index}",
            "resolution": f"{self.frame_width}x{self.frame_height}",
            "fps_target": int(self.fps),
            "fps_actual": float(health.get('fps_actual', 0)),
            "ir_mode": bool(self.ir_mode),
            "auto_ir": bool(self.auto_ir),
            "quality": int(self.quality),
            "uptime": float(health.get('uptime', 0)),
            "frame_count": int(health.get('frame_count', 0)),
            "error_count": int(health.get('error_count', 0)),
            "last_error": health.get('last_error'),
            "recovery_attempts": int(self.recovery_attempts),
            "max_recovery_attempts": int(self.max_recovery_attempts),
            "last_check": health.get('last_check'),
            "connection_status": str(health.get('connection_status', 'unknown'))
        }
        
        return convert_numpy_types(status)

# Global camera manager instance
camera_manager = None

def get_camera_manager() -> Optional[CameraManager]:
    """Get global camera manager instance"""
    global camera_manager
    return camera_manager

def init_camera_manager() -> CameraManager:
    """Initialize global camera manager"""
    global camera_manager
    if camera_manager is None:
        camera_manager = CameraManager()
    return camera_manager

def stop_camera_manager():
    """Stop global camera manager"""
    global camera_manager
    if camera_manager:
        camera_manager.stop()
        camera_manager = None 