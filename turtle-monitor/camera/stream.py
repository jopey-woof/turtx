#!/usr/bin/env python3
"""
🐢 Turtle Monitor Camera Streaming Service
Dedicated service for camera streaming with enhanced reliability
"""

import os
import cv2
import time
import logging
import threading
import signal
import sys
from typing import Optional
from datetime import datetime
import json
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CameraStreamService:
    """Dedicated camera streaming service"""
    
    def __init__(self):
        self.camera = None
        self.camera_index = 0
        self.is_running = False
        self.frame_width = 1280  # Stream resolution
        self.frame_height = 720
        self.fps = 15
        self.quality = 70  # JPEG quality for streaming
        self.ir_mode = False
        self.auto_ir = True
        
        # Health monitoring
        self.health_data = {
            'start_time': datetime.now(),
            'frame_count': 0,
            'error_count': 0,
            'last_error': None,
            'connection_status': 'disconnected',
            'fps_actual': 0,
            'last_frame_time': None
        }
        
        # Threading
        self.lock = threading.Lock()
        self.stream_thread = None
        self.health_thread = None
        
        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def init_camera(self) -> bool:
        """Initialize camera connection"""
        try:
            logger.info(f"🎥 Initializing camera at index {self.camera_index}")
            
            # Find camera device
            camera_device = self.find_camera_device()
            if camera_device:
                logger.info(f"Found camera device: {camera_device}")
            
            # Initialize OpenCV camera
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera at index {self.camera_index}")
                return False
            
            # Set camera properties for streaming
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Set camera settings for turtle monitoring
            self.set_camera_settings()
            
            # Test camera
            ret, frame = self.camera.read()
            if not ret or frame is None:
                logger.error("Failed to capture test frame")
                self.camera.release()
                return False
            
            self.health_data['connection_status'] = 'connected'
            self.health_data['last_frame_time'] = time.time()
            
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
            camera_paths = ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]
            
            for path in camera_paths:
                if os.path.exists(path):
                    logger.info(f"Found camera device: {path}")
                    return path
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding camera device: {e}")
            return None
    
    def set_camera_settings(self):
        """Set camera settings for optimal turtle monitoring"""
        try:
            if not self.camera or not self.camera.isOpened():
                return
            
            # Camera settings optimized for turtle habitat monitoring
            settings = {
                'brightness': 50,
                'contrast': 50,
                'saturation': 60,  # Slightly higher for better color
                'hue': 0,
                'gain': 50,
                'exposure': -6,  # Auto exposure
                'focus': 0,  # Auto focus
                'white_balance': 4600,  # Auto white balance
            }
            
            for setting, value in settings.items():
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
                    elif setting == 'exposure':
                        self.camera.set(cv2.CAP_PROP_EXPOSURE, value)
                    elif setting == 'focus':
                        self.camera.set(cv2.CAP_PROP_FOCUS, value)
                    elif setting == 'white_balance':
                        self.camera.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, value)
                except Exception as e:
                    logger.warning(f"Failed to set {setting}: {e}")
            
            logger.info("Camera settings configured for turtle monitoring")
            
        except Exception as e:
            logger.error(f"Error setting camera properties: {e}")
    
    def get_frame(self) -> Optional[bytes]:
        """Get frame as JPEG bytes for streaming"""
        try:
            with self.lock:
                if not self.camera or not self.camera.isOpened():
                    return None
                
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    logger.warning("Failed to capture frame")
                    return None
                
                # Update health data
                current_time = time.time()
                self.health_data['frame_count'] += 1
                self.health_data['last_frame_time'] = current_time
                
                # Calculate actual FPS
                if self.health_data['last_frame_time']:
                    time_diff = current_time - self.health_data['last_frame_time']
                    if time_diff > 0:
                        self.health_data['fps_actual'] = 1.0 / time_diff
                
                # Auto IR mode detection
                if self.auto_ir:
                    self.detect_ir_mode(frame)
                
                # Encode as JPEG for streaming
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
                ret, jpeg_data = cv2.imencode('.jpg', frame, encode_param)
                
                if not ret:
                    logger.error("Failed to encode JPEG")
                    return None
                
                return jpeg_data.tobytes()
                
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
            self.health_data['last_error'] = str(e)
            self.health_data['error_count'] += 1
            return None
    
    def detect_ir_mode(self, frame):
        """Detect if camera is in IR mode"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:, :, 1])
            
            was_ir = self.ir_mode
            self.ir_mode = (avg_brightness < 80 and saturation < 30)
            
            if was_ir != self.ir_mode:
                logger.info(f"IR mode {'enabled' if self.ir_mode else 'disabled'}")
            
        except Exception as e:
            logger.warning(f"Error detecting IR mode: {e}")
    
    def start_streaming(self):
        """Start camera streaming service"""
        try:
            if self.is_running:
                logger.warning("Streaming service already running")
                return
            
            if not self.init_camera():
                logger.error("Failed to initialize camera")
                return
            
            self.is_running = True
            logger.info("🎥 Camera streaming service started")
            
            # Start health monitoring thread
            self.health_thread = threading.Thread(target=self._health_monitor, daemon=True)
            self.health_thread.start()
            
            # Main streaming loop
            while self.is_running:
                try:
                    frame_data = self.get_frame()
                    if frame_data:
                        # In a real implementation, this would send to a queue or socket
                        # For now, we just simulate streaming
                        time.sleep(1.0 / self.fps)
                    else:
                        time.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"Error in streaming loop: {e}")
                    time.sleep(1.0)
                    
        except Exception as e:
            logger.error(f"Error starting streaming service: {e}")
        finally:
            self.stop()
    
    def _health_monitor(self):
        """Health monitoring thread"""
        while self.is_running:
            try:
                # Check camera health
                if self.camera and self.camera.isOpened():
                    ret, frame = self.camera.read()
                    if ret and frame is not None:
                        self.health_data['connection_status'] = 'connected'
                    else:
                        self.health_data['connection_status'] = 'error'
                        logger.warning("Camera health check failed")
                else:
                    self.health_data['connection_status'] = 'disconnected'
                
                # Log health status periodically
                if self.health_data['frame_count'] % 300 == 0:  # Every 300 frames
                    logger.info(f"Health: {self.health_data['connection_status']}, "
                              f"FPS: {self.health_data['fps_actual']:.1f}, "
                              f"Frames: {self.health_data['frame_count']}")
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                time.sleep(5)
    
    def get_health(self) -> dict:
        """Get health status"""
        return self.health_data.copy()
    
    def stop(self):
        """Stop streaming service"""
        logger.info("🛑 Stopping camera streaming service...")
        
        self.is_running = False
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.health_data['connection_status'] = 'disconnected'
        logger.info("Camera streaming service stopped")

def main():
    """Main function"""
    logger.info("🐢 Starting Turtle Monitor Camera Streaming Service")
    
    service = CameraStreamService()
    
    try:
        service.start_streaming()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Service error: {e}")
    finally:
        service.stop()

if __name__ == "__main__":
    main() 