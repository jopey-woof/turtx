#!/usr/bin/env python3
"""
🐢 Turtle Camera Manager
Advanced camera management for Arducam 1080P USB camera with full feature support
"""

import cv2
import time
import threading
import logging
import subprocess
import tempfile
import os
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

def run_with_timeout(cmd, timeout=5.0, capture_output=True):
    """Run subprocess command with timeout"""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, timeout=timeout)
        return result
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Command timeout after {timeout}s: {' '.join(cmd)}")
        return None
    except Exception as e:
        logger.error(f"❌ Command failed: {' '.join(cmd)} - {e}")
        return None

class IRFilterMode(Enum):
    """IR filter control modes"""
    AUTO = "auto"
    DAY = "day"
    NIGHT = "night"

class CameraPreset(Enum):
    """Camera preset configurations"""
    DAYLIGHT = "daylight"
    NIGHT_VISION = "night_vision"
    AUTO = "auto"
    CUSTOM = "custom"

@dataclass
class CameraSettings:
    """Camera settings configuration"""
    # Resolution settings
    streaming_resolution: Tuple[int, int] = (1280, 720)
    snapshot_resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    
    # Exposure settings
    exposure_mode: str = "auto"  # "auto", "manual"
    exposure_time: int = 156  # 1-5000
    gain: int = 15  # 0-100
    
    # White balance settings
    white_balance_auto: bool = True
    white_balance_temperature: int = 4600  # 2800-6500K
    
    # Image quality settings
    brightness: int = 25  # -64 to 64
    contrast: int = 64  # 0-64
    saturation: int = 55  # 0-128
    sharpness: int = 3  # 0-6
    gamma: int = 100  # 72-500
    
    # Advanced settings
    backlight_compensation: int = 1  # 0-2
    power_line_frequency: int = 1  # 0=Disabled, 1=50Hz, 2=60Hz
    
    # IR filter settings
    ir_filter_mode: IRFilterMode = IRFilterMode.AUTO

class TurtleCameraManager:
    """
    Advanced camera manager for Arducam 1080P USB camera
    Supports full resolution streaming, snapshots, and advanced controls
    """
    
    def __init__(self, device_path: str = "/dev/video0"):
        self.device_path = device_path
        self.camera = None
        self.is_connected = False
        self.is_streaming = False
        self.stream_thread = None
        self.stream_stop_event = threading.Event()
        
        # Camera settings
        self.settings = CameraSettings()
        
        # Performance tracking
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.frame_count = 0
        
        # Thread safety
        self.camera_lock = threading.Lock()
        self.settings_lock = threading.Lock()
        
        # Current frame buffer
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # Initialize camera (non-blocking)
        try:
            self._initialize_camera()
        except Exception as e:
            logger.error(f"❌ Camera initialization failed: {e}")
            self.is_connected = False
    
    def _initialize_camera(self) -> bool:
        """Initialize camera connection and settings"""
        try:
            # Test both camera devices
            devices = {
                "/dev/video0": "MJPG",  # For streaming
                "/dev/video2": "H264"   # For snapshots
            }
            
            working_devices = {}
            
            for device, format_type in devices.items():
                try:
                    logger.info(f"🔍 Testing {device} ({format_type})")
                    
                    # Test with FFmpeg
                    test_cmd = [
                        'ffmpeg', '-f', 'v4l2',
                        '-video_size', f'{self.settings.streaming_resolution[0]}x{self.settings.streaming_resolution[1]}',
                        '-i', device,
                        '-vframes', '1',
                        '-f', 'null',
                        '-'
                    ]
                    
                    result = run_with_timeout(test_cmd, timeout=3.0)
                    if result and result.returncode == 0:
                        working_devices[device] = format_type
                        logger.info(f"✅ {device} ({format_type}) works!")
                    else:
                        logger.warning(f"⚠️ {device} test failed")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Exception testing {device}: {e}")
                    continue
            
            if not working_devices:
                logger.error("❌ No camera devices work, using placeholder mode")
                self.is_connected = True
                self.device_path = "/dev/video0"
                logger.info("✅ Camera manager initialized in placeholder mode")
                return True
            
            # Use the best available device
            if "/dev/video0" in working_devices:
                self.device_path = "/dev/video0"  # MJPG for streaming
                logger.info("✅ Using /dev/video0 (MJPG) for streaming")
            elif "/dev/video2" in working_devices:
                self.device_path = "/dev/video2"  # H264 for snapshots
                logger.info("✅ Using /dev/video2 (H264) for snapshots")
            
            self.is_connected = True
            logger.info(f"✅ Camera manager initialized with {self.device_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Camera initialization failed: {e}")
            self.is_connected = False
            return False
    
    def _apply_camera_settings(self):
        """Apply current camera settings to hardware"""
        try:
            if not self.camera or not self.is_connected:
                return
            
            with self.settings_lock:
                # Exposure settings
                if self.settings.exposure_mode == "auto":
                    self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Auto mode
                else:
                    self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)  # Manual mode
                    self.camera.set(cv2.CAP_PROP_EXPOSURE, self.settings.exposure_time)
                
                # Gain
                self.camera.set(cv2.CAP_PROP_GAIN, self.settings.gain)
                
                # White balance
                if self.settings.white_balance_auto:
                    self.camera.set(cv2.CAP_PROP_AUTO_WB, 1.0)
                else:
                    self.camera.set(cv2.CAP_PROP_AUTO_WB, 0.0)
                    # Note: Temperature setting requires v4l2-ctl
                
                # Brightness and contrast
                self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.settings.brightness)
                self.camera.set(cv2.CAP_PROP_CONTRAST, self.settings.contrast)
                
                # Saturation and hue
                self.camera.set(cv2.CAP_PROP_SATURATION, self.settings.saturation)
                self.camera.set(cv2.CAP_PROP_HUE, 0)  # Default hue
                
                # Gamma
                self.camera.set(cv2.CAP_PROP_GAMMA, self.settings.gamma)
                
                logger.debug("✅ Camera settings applied successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to apply camera settings: {e}")
    
    def _apply_v4l2_settings(self):
        """Apply advanced settings using v4l2-ctl"""
        try:
            with self.settings_lock:
                # White balance temperature (if not auto)
                if not self.settings.white_balance_auto:
                    result = run_with_timeout([
                        'v4l2-ctl', '-d', self.device_path,
                        '--set-ctrl=white_balance_temperature_auto=0',
                        '--set-ctrl=white_balance_temperature=' + str(self.settings.white_balance_temperature)
                    ], timeout=2.0)
                    if result and result.returncode != 0:
                        logger.warning("⚠️ White balance setting failed")
                
                # Sharpness
                result = run_with_timeout([
                    'v4l2-ctl', '-d', self.device_path,
                    '--set-ctrl=sharpness=' + str(self.settings.sharpness)
                ], timeout=2.0)
                if result and result.returncode != 0:
                    logger.warning("⚠️ Sharpness setting failed")
                
                # Backlight compensation
                result = run_with_timeout([
                    'v4l2-ctl', '-d', self.device_path,
                    '--set-ctrl=backlight_compensation=' + str(self.settings.backlight_compensation)
                ], timeout=2.0)
                if result and result.returncode != 0:
                    logger.warning("⚠️ Backlight compensation setting failed")
                
                # Power line frequency
                result = run_with_timeout([
                    'v4l2-ctl', '-d', self.device_path,
                    '--set-ctrl=power_line_frequency=' + str(self.settings.power_line_frequency)
                ], timeout=2.0)
                if result and result.returncode != 0:
                    logger.warning("⚠️ Power line frequency setting failed")
                
                logger.debug("✅ V4L2 settings applied successfully")
                
        except Exception as e:
            logger.error(f"❌ V4L2 settings application failed: {e}")
    
    def start_streaming(self) -> bool:
        """Start camera streaming in background thread"""
        if self.is_streaming:
            logger.warning("⚠️ Camera already streaming")
            return True
        
        if not self.is_connected:
            if not self._initialize_camera():
                return False
        
        try:
            self.stream_stop_event.clear()
            self.stream_thread = threading.Thread(target=self._stream_worker, daemon=True)
            self.stream_thread.start()
            self.is_streaming = True
            
            logger.info("🎥 Camera streaming started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start camera streaming: {e}")
            return False
    
    def stop_streaming(self):
        """Stop camera streaming"""
        if not self.is_streaming:
            return
        
        try:
            self.stream_stop_event.set()
            if self.stream_thread:
                self.stream_thread.join(timeout=5.0)
            
            self.is_streaming = False
            logger.info("🛑 Camera streaming stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping camera streaming: {e}")
    
    def _stream_worker(self):
        """Background worker for camera streaming"""
        logger.info("🎬 Camera stream worker started")
        
        while not self.stream_stop_event.is_set():
            try:
                with self.camera_lock:
                    if not self.camera or not self.is_connected:
                        time.sleep(0.1)
                        continue
                    
                    ret, frame = self.camera.read()
                    if ret and frame is not None:
                        with self.frame_lock:
                            self.current_frame = frame.copy()
                        
                        # Update FPS counter
                        self.frame_count += 1
                        current_time = time.time()
                        if current_time - self.last_fps_time >= 1.0:
                            self.fps_counter = self.frame_count
                            self.frame_count = 0
                            self.last_fps_time = current_time
                    else:
                        logger.warning("⚠️ Failed to read frame from camera")
                        time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error in camera stream worker: {e}")
                time.sleep(0.1)
        
        logger.info("🎬 Camera stream worker stopped")
    
    def get_current_frame(self) -> Optional[bytes]:
        """Get current frame as JPEG bytes"""
        try:
            if not self.is_connected:
                return self._get_placeholder_image()
            
            # Use FFmpeg to capture a frame from the camera
            return self.capture_ffmpeg_snapshot(self.settings.streaming_resolution)
            
        except Exception as e:
            logger.error(f"❌ Error getting current frame: {e}")
            return self._get_placeholder_image()
    
    def _get_placeholder_image(self) -> bytes:
        """Generate a placeholder image when camera is unavailable"""
        try:
            # Create a simple placeholder image
            width, height = self.settings.streaming_resolution
            img = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add some text
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = "Camera Unavailable"
            text_size = cv2.getTextSize(text, font, 1, 2)[0]
            text_x = (width - text_size[0]) // 2
            text_y = (height + text_size[1]) // 2
            
            cv2.putText(img, text, (text_x, text_y), font, 1, (255, 255, 255), 2)
            
            # Encode as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            ret, jpeg_data = cv2.imencode('.jpg', img, encode_param)
            
            if ret:
                return jpeg_data.tobytes()
            else:
                return b''
                
        except Exception as e:
            logger.error(f"❌ Error creating placeholder image: {e}")
            return b''
    
    def capture_snapshot(self, resolution: Optional[Tuple[int, int]] = None) -> Optional[bytes]:
        """Capture high-quality snapshot at specified resolution"""
        try:
            if not self.is_connected:
                if not self._initialize_camera():
                    return None
            
            # Set resolution for snapshot
            snapshot_res = resolution or self.settings.snapshot_resolution
            
            with self.camera_lock:
                # Temporarily change resolution
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, snapshot_res[0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, snapshot_res[1])
                
                # Capture frame
                ret, frame = self.camera.read()
                
                if not ret or frame is None:
                    logger.error("❌ Failed to capture snapshot")
                    return None
                
                # Encode as high-quality JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]  # 95% quality for snapshots
                ret, jpeg_data = cv2.imencode('.jpg', frame, encode_param)
                
                # Restore streaming resolution
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.streaming_resolution[0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.streaming_resolution[1])
                
                if ret:
                    logger.info(f"📸 Snapshot captured at {snapshot_res[0]}x{snapshot_res[1]}")
                    return jpeg_data.tobytes()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error capturing snapshot: {e}")
            return None
    
    def capture_ffmpeg_snapshot(self, resolution: Optional[Tuple[int, int]] = None) -> Optional[bytes]:
        """Capture snapshot using FFmpeg for maximum quality"""
        try:
            snapshot_res = resolution or self.settings.snapshot_resolution
            
            # Choose the best device based on resolution
            if snapshot_res[0] >= 1920:  # High resolution - use H264 device
                device = "/dev/video2"
                logger.debug(f"📸 Using {device} (H264) for high-res snapshot")
            else:  # Lower resolution - use MJPG device
                device = "/dev/video0"
                logger.debug(f"📸 Using {device} (MJPG) for snapshot")
            
            # Use FFmpeg to capture high-quality snapshot
            cmd = [
                'ffmpeg',
                '-f', 'v4l2',
                '-video_size', f'{snapshot_res[0]}x{snapshot_res[1]}',
                '-i', device,
                '-vframes', '1',
                '-q:v', '2',  # High quality
                '-f', 'image2',
                'pipe:1'
            ]
            
            result = run_with_timeout(cmd, timeout=3.0)
            if result is None:
                logger.error("❌ FFmpeg snapshot timeout")
                return None
                
            if result.returncode == 0 and result.stdout:
                logger.info(f"📸 FFmpeg snapshot captured at {snapshot_res[0]}x{snapshot_res[1]} from {device}")
                return result.stdout
            else:
                logger.error(f"❌ FFmpeg snapshot failed: {result.stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error capturing FFmpeg snapshot: {e}")
            return None
    
    def set_resolution(self, resolution: Tuple[int, int], is_streaming: bool = True):
        """Set camera resolution"""
        try:
            with self.settings_lock:
                if is_streaming:
                    self.settings.streaming_resolution = resolution
                else:
                    self.settings.snapshot_resolution = resolution
                
                # Apply immediately if streaming
                if self.is_streaming and is_streaming:
                    with self.camera_lock:
                        if self.camera:
                            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
                            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
                
                logger.info(f"📐 Resolution set to {resolution[0]}x{resolution[1]} ({'streaming' if is_streaming else 'snapshot'})")
                
        except Exception as e:
            logger.error(f"❌ Error setting resolution: {e}")
    
    def set_exposure(self, mode: str, value: Optional[int] = None):
        """Set camera exposure settings"""
        try:
            with self.settings_lock:
                self.settings.exposure_mode = mode
                if value is not None:
                    self.settings.exposure_time = value
                
                # Apply settings
                self._apply_camera_settings()
                
                logger.info(f"🌅 Exposure set to {mode} mode" + (f" (value: {value})" if value else ""))
                
        except Exception as e:
            logger.error(f"❌ Error setting exposure: {e}")
    
    def set_gain(self, gain: int):
        """Set camera gain"""
        try:
            with self.settings_lock:
                self.settings.gain = max(0, min(100, gain))
                
                # Apply settings
                self._apply_camera_settings()
                
                logger.info(f"📈 Gain set to {self.settings.gain}")
                
        except Exception as e:
            logger.error(f"❌ Error setting gain: {e}")
    
    def set_white_balance(self, auto: bool, temperature: Optional[int] = None):
        """Set white balance settings"""
        try:
            with self.settings_lock:
                self.settings.white_balance_auto = auto
                if temperature is not None:
                    self.settings.white_balance_temperature = max(2800, min(6500, temperature))
                
                # Apply settings
                self._apply_camera_settings()
                self._apply_v4l2_settings()
                
                mode = "auto" if auto else f"manual ({temperature}K)"
                logger.info(f"🎨 White balance set to {mode}")
                
        except Exception as e:
            logger.error(f"❌ Error setting white balance: {e}")
    
    def set_image_quality(self, brightness: Optional[int] = None, contrast: Optional[int] = None,
                         saturation: Optional[int] = None, sharpness: Optional[int] = None):
        """Set image quality parameters"""
        try:
            with self.settings_lock:
                if brightness is not None:
                    self.settings.brightness = max(-64, min(64, brightness))
                if contrast is not None:
                    self.settings.contrast = max(0, min(64, contrast))
                if saturation is not None:
                    self.settings.saturation = max(0, min(128, saturation))
                if sharpness is not None:
                    self.settings.sharpness = max(0, min(6, sharpness))
                
                # Apply settings
                self._apply_camera_settings()
                self._apply_v4l2_settings()
                
                logger.info("🎨 Image quality settings updated")
                
        except Exception as e:
            logger.error(f"❌ Error setting image quality: {e}")
    
    def set_ir_filter(self, mode: IRFilterMode):
        """Set IR filter mode (placeholder for GPIO control)"""
        try:
            with self.settings_lock:
                self.settings.ir_filter_mode = mode
                
                # TODO: Implement GPIO control for IR filter
                # This would control GPIO pins to switch IR filter hardware
                
                logger.info(f"🌙 IR filter set to {mode.value} mode")
                
        except Exception as e:
            logger.error(f"❌ Error setting IR filter: {e}")
    
    def apply_preset(self, preset: CameraPreset):
        """Apply camera preset configuration"""
        try:
            with self.settings_lock:
                if preset == CameraPreset.DAYLIGHT:
                    self.settings.exposure_mode = "auto"
                    self.settings.gain = 10
                    self.settings.white_balance_auto = True
                    self.settings.brightness = 20
                    self.settings.contrast = 60
                    self.settings.saturation = 60
                    self.settings.ir_filter_mode = IRFilterMode.DAY
                    
                elif preset == CameraPreset.NIGHT_VISION:
                    self.settings.exposure_mode = "manual"
                    self.settings.exposure_time = 500
                    self.settings.gain = 80
                    self.settings.white_balance_auto = False
                    self.settings.white_balance_temperature = 3000
                    self.settings.brightness = 30
                    self.settings.contrast = 70
                    self.settings.saturation = 40
                    self.settings.ir_filter_mode = IRFilterMode.NIGHT
                    
                elif preset == CameraPreset.AUTO:
                    self.settings.exposure_mode = "auto"
                    self.settings.gain = 15
                    self.settings.white_balance_auto = True
                    self.settings.brightness = 25
                    self.settings.contrast = 64
                    self.settings.saturation = 55
                    self.settings.ir_filter_mode = IRFilterMode.AUTO
                
                # Apply all settings
                self._apply_camera_settings()
                self._apply_v4l2_settings()
                
                logger.info(f"⚙️ Applied camera preset: {preset.value}")
                
        except Exception as e:
            logger.error(f"❌ Error applying camera preset: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get camera status and information"""
        try:
            status = {
                "connected": self.is_connected,
                "streaming": self.is_streaming,
                "device": self.device_path,
                "fps": self.fps_counter,
                "resolution": {
                    "streaming": self.settings.streaming_resolution,
                    "snapshot": self.settings.snapshot_resolution
                },
                "settings": {
                    "exposure_mode": self.settings.exposure_mode,
                    "exposure_time": self.settings.exposure_time,
                    "gain": self.settings.gain,
                    "white_balance_auto": self.settings.white_balance_auto,
                    "white_balance_temperature": self.settings.white_balance_temperature,
                    "brightness": self.settings.brightness,
                    "contrast": self.settings.contrast,
                    "saturation": self.settings.saturation,
                    "sharpness": self.settings.sharpness,
                    "ir_filter_mode": self.settings.ir_filter_mode.value
                },
                "capabilities": {
                    "resolutions": [
                        (1920, 1080),
                        (1280, 720),
                        (640, 480),
                        (320, 240)
                    ],
                    "max_fps": 30,
                    "formats": ["MJPG", "YUYV"]
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting camera status: {e}")
            return {"connected": False, "error": str(e)}
    
    def restart(self) -> bool:
        """Restart camera connection"""
        try:
            logger.info("🔄 Restarting camera connection...")
            
            # Stop streaming
            self.stop_streaming()
            
            # Reinitialize camera
            success = self._initialize_camera()
            
            if success:
                logger.info("✅ Camera restart successful")
            else:
                logger.error("❌ Camera restart failed")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error restarting camera: {e}")
            return False
    
    def stop(self):
        """Stop camera and cleanup resources"""
        try:
            logger.info("🛑 Stopping camera manager...")
            
            # Stop streaming
            self.stop_streaming()
            
            # Release camera
            with self.camera_lock:
                if self.camera:
                    self.camera.release()
                    self.camera = None
            
            self.is_connected = False
            logger.info("✅ Camera manager stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping camera manager: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.stop() 