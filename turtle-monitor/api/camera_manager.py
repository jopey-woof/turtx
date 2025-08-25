#!/usr/bin/env python3
"""
🐢 Turtle Camera Manager
Advanced camera management for Arducam 1080P USB camera with full feature support
"""

import cv2
import numpy as np
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
        
        # Continuous stream management
        self.stream_process = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.last_frame_time = 0
        
        # Initialize camera (non-blocking)
        try:
            self._initialize_camera()
        except Exception as e:
            logger.error(f"❌ Camera initialization failed: {e}")
            self.is_connected = False
    
    def _initialize_camera(self) -> bool:
        """Initialize camera connection and settings (non-blocking)"""
        try:
            # Quick check if camera devices exist
            devices = ["/dev/video0", "/dev/video1", "/dev/video2", "/dev/video3"]
            available_devices = []
            
            for device in devices:
                if os.path.exists(device):
                    available_devices.append(device)
            
            if not available_devices:
                logger.warning("⚠️ No camera devices found, using placeholder mode")
                self.is_connected = True
                self.device_path = "/dev/video0"
                logger.info("✅ Camera manager initialized in placeholder mode")
                return True
            
            # Use the first available device without testing
            self.device_path = available_devices[0]
            self.is_connected = True
            logger.info(f"✅ Camera manager initialized with {self.device_path} (quick mode)")
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
        """Start continuous camera streaming"""
        if self.is_streaming:
            logger.warning("⚠️ Camera already streaming")
            return True
        
        if not self.is_connected:
            if not self._initialize_camera():
                return False
        
        try:
            # Start continuous stream
            if self._start_continuous_stream():
                self.is_streaming = True
                logger.info("🎥 Continuous camera streaming started")
                return True
            else:
                logger.error("❌ Failed to start continuous stream")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start camera streaming: {e}")
            return False
    
    def stop_streaming(self):
        """Stop camera streaming"""
        if not self.is_streaming:
            return
        
        try:
            self._stop_continuous_stream()
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
    
    def _start_continuous_stream(self):
        """Start a continuous FFmpeg stream process"""
        try:
            if hasattr(self, '_stream_process') and self._stream_process:
                self._stop_continuous_stream()
            
            # Start FFmpeg in continuous mode for MJPEG streaming
            cmd = [
                'ffmpeg',
                '-f', 'v4l2',
                '-input_format', 'mjpeg',
                '-video_size', f'{self.settings.streaming_resolution[0]}x{self.settings.streaming_resolution[1]}',
                '-i', self.device_path,
                '-f', 'mjpeg',  # Output MJPEG format
                '-q:v', '10',   # Good quality for streaming
                '-r', '15',     # 15 FPS
                'pipe:1'
            ]
            
            self._stream_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
            logger.info("✅ Continuous camera stream started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start continuous stream: {e}")
            self._stream_process = None
    
    def _stop_continuous_stream(self):
        """Stop the continuous FFmpeg stream process"""
        try:
            if hasattr(self, '_stream_process') and self._stream_process:
                self._stream_process.terminate()
                self._stream_process.wait(timeout=2)
                self._stream_process = None
                logger.info("🛑 Continuous camera stream stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping continuous stream: {e}")
    
    def _get_frame_from_stream(self) -> Optional[bytes]:
        """Extract a single frame from the continuous MJPEG stream"""
        try:
            if not hasattr(self, '_stream_process') or not self._stream_process:
                return None
            
            # Read MJPEG frame from the stream
            # MJPEG format: --boundary\r\nContent-Type: image/jpeg\r\nContent-Length: size\r\n\r\n[image data]\r\n
            
            # Read until we find a frame boundary
            frame_data = b""
            boundary_found = False
            
            while not boundary_found:
                line = self._stream_process.stdout.readline()
                if not line:
                    break
                
                if line.startswith(b'--'):
                    boundary_found = True
                    frame_data = line
            
            if not boundary_found:
                return None
            
            # Read headers
            while True:
                line = self._stream_process.stdout.readline()
                if not line or line == b'\r\n':
                    break
                frame_data += line
            
            # Read image data
            content_length = 0
            for line in frame_data.split(b'\r\n'):
                if line.startswith(b'Content-Length:'):
                    try:
                        content_length = int(line.split(b':')[1].strip())
                        break
                    except:
                        pass
            
            if content_length > 0:
                image_data = self._stream_process.stdout.read(content_length)
                frame_data += image_data
                
                # Read the trailing \r\n
                self._stream_process.stdout.read(2)
                
                return image_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error reading frame from stream: {e}")
            return None
    
    def get_current_frame(self) -> Optional[bytes]:
        """Get current frame directly from camera - always available"""
        try:
            if not self.is_connected:
                return self._get_placeholder_image()
            
            # Try the continuous stream first
            frame_data = self._get_direct_frame()
            
            # If continuous stream fails, try simple capture
            if frame_data is None or frame_data == self._get_placeholder_image():
                frame_data = self._get_simple_frame()
            
            # If we successfully get a frame, mark as streaming
            if frame_data and frame_data != self._get_placeholder_image():
                self.is_streaming = True
            
            return frame_data
                    
        except Exception as e:
            logger.error(f"❌ Error getting current frame: {e}")
            return self._get_placeholder_image()
    
    def _get_simple_frame(self) -> Optional[bytes]:
        """Get frame using simple FFmpeg command - fallback method"""
        try:
            # Simple FFmpeg command for single frame capture
            cmd = [
                'ffmpeg',
                '-f', 'v4l2',
                '-input_format', 'mjpeg',
                '-video_size', f'{self.settings.streaming_resolution[0]}x{self.settings.streaming_resolution[1]}',
                '-i', self.device_path,
                '-vframes', '1',
                '-q:v', '10',  # Good quality
                '-f', 'image2',
                'pipe:1'
            ]
            
            result = run_with_timeout(cmd, timeout=1.5)  # Shorter timeout
            if result and result.returncode == 0 and result.stdout:
                logger.debug("✅ Simple frame capture successful")
                return result.stdout
            else:
                logger.debug("⚠️ Simple frame capture failed")
                return self._get_placeholder_image()
                
        except Exception as e:
            logger.debug(f"❌ Simple frame capture error: {e}")
            return self._get_placeholder_image()
    
    def _get_direct_frame(self) -> Optional[bytes]:
        """Get frame directly from camera using FFmpeg - improved for streaming"""
        try:
            # Use a more efficient approach for streaming
            # Instead of calling FFmpeg for each frame, use a continuous stream
            if not hasattr(self, '_stream_process') or self._stream_process is None:
                self._start_continuous_stream()
            
            # Get frame from the continuous stream
            frame_data = self._get_frame_from_stream()
            if frame_data:
                logger.debug("✅ Frame captured from continuous stream")
                self.is_streaming = True
                return frame_data
            else:
                logger.warning("⚠️ No frame from continuous stream, using placeholder")
                return self._get_placeholder_image()
                
        except Exception as e:
            logger.error(f"❌ Direct frame capture error: {e}")
            return self._get_placeholder_image()
    
    def capture_snapshot(self, resolution: Optional[Tuple[int, int]] = None) -> Optional[bytes]:
        """Capture snapshot from current stream frame"""
        try:
            # Get current frame from stream
            frame_data = self.get_current_frame()
            if not frame_data or frame_data == self._get_placeholder_image():
                logger.warning("⚠️ No valid frame for snapshot")
                return None
            
            # If we need a different resolution, we could resize here
            # For now, return the current frame
            logger.info("📸 Snapshot captured from stream")
            return frame_data
            
        except Exception as e:
            logger.error(f"❌ Error capturing snapshot: {e}")
            return None
    
    def capture_ffmpeg_snapshot(self, resolution: Optional[Tuple[int, int]] = None) -> Optional[bytes]:
        """Capture high-quality snapshot using separate FFmpeg process with current camera settings"""
        try:
            snapshot_res = resolution or self.settings.snapshot_resolution
            
            # Get current camera settings from simple_camera_controls
            from simple_camera_controls import camera_controls
            current_settings = camera_controls.get_all_controls()
            
            # Build FFmpeg command with camera controls
            cmd = [
                'ffmpeg',
                '-f', 'v4l2',
                '-input_format', 'mjpeg',
                '-video_size', f'{snapshot_res[0]}x{snapshot_res[1]}',
                '-i', self.device_path,
                '-vframes', '1',
                '-q:v', '2',  # High quality
            ]
            
            # Add camera controls if available
            if current_settings:
                # Apply brightness, contrast, saturation, etc.
                if 'brightness' in current_settings:
                    cmd.extend(['-vf', f'eq=brightness={current_settings["brightness"]/64.0:.3f}'])
                if 'contrast' in current_settings:
                    cmd.extend(['-vf', f'eq=contrast={current_settings["contrast"]/32.0:.3f}'])
                if 'saturation' in current_settings:
                    cmd.extend(['-vf', f'eq=saturation={current_settings["saturation"]/64.0:.3f}'])
                if 'gamma' in current_settings:
                    cmd.extend(['-vf', f'eq=gamma={current_settings["gamma"]/100.0:.3f}'])
            
            cmd.extend(['-f', 'image2', 'pipe:1'])
            
            result = run_with_timeout(cmd, timeout=3.0)
            if result and result.returncode == 0 and result.stdout:
                logger.info(f"📸 High-quality snapshot captured at {snapshot_res[0]}x{snapshot_res[1]} with camera settings")
                return result.stdout
            else:
                logger.warning("⚠️ High-quality snapshot failed, using stream frame")
                return self.capture_snapshot(resolution)
                
        except Exception as e:
            logger.error(f"❌ Error capturing high-quality snapshot: {e}")
            return self.capture_snapshot(resolution)
    
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