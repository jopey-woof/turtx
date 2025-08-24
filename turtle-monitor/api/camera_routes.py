#!/usr/bin/env python3
"""
🐢 Turtle Camera API Routes
FastAPI routes for camera management and control
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from fastapi import APIRouter, HTTPException, Body, Path, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from camera_manager import TurtleCameraManager, IRFilterMode, CameraPreset

logger = logging.getLogger(__name__)

# Create router
camera_router = APIRouter(prefix="/api/camera", tags=["camera"])

# Global camera manager instance
camera_manager: Optional[TurtleCameraManager] = None

def get_camera_manager() -> TurtleCameraManager:
    """Get camera manager instance"""
    global camera_manager
    if not camera_manager:
        raise HTTPException(status_code=503, detail="Camera manager not initialized")
    return camera_manager

# Pydantic models for request/response
class CameraSettingsRequest(BaseModel):
    """Camera settings update request"""
    exposure_mode: Optional[str] = None
    exposure_time: Optional[int] = None
    gain: Optional[int] = None
    white_balance_auto: Optional[bool] = None
    white_balance_temperature: Optional[int] = None
    brightness: Optional[int] = None
    contrast: Optional[int] = None
    saturation: Optional[int] = None
    sharpness: Optional[int] = None

class ResolutionRequest(BaseModel):
    """Resolution change request"""
    width: int
    height: int
    is_streaming: bool = True

class IRFilterRequest(BaseModel):
    """IR filter control request"""
    mode: str  # "auto", "day", "night"

class PresetRequest(BaseModel):
    """Camera preset request"""
    preset: str  # "daylight", "night_vision", "auto", "custom"

@camera_router.get("/status")
async def camera_status():
    """Get camera health and connection status"""
    try:
        camera_mgr = get_camera_manager()
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "camera": status,
            "status": "online" if status.get("connected", False) else "offline"
        }
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        raise HTTPException(status_code=500, detail=f"Camera status error: {str(e)}")

@camera_router.get("/capabilities")
async def camera_capabilities():
    """Get camera capabilities and supported features"""
    try:
        camera_mgr = get_camera_manager()
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "capabilities": status.get("capabilities", {}),
            "device": status.get("device", ""),
            "supported_controls": {
                "exposure": {"auto": True, "manual": True, "range": [1, 5000]},
                "gain": {"range": [0, 100]},
                "white_balance": {"auto": True, "manual": True, "temperature_range": [2800, 6500]},
                "brightness": {"range": [-64, 64]},
                "contrast": {"range": [0, 64]},
                "saturation": {"range": [0, 128]},
                "sharpness": {"range": [0, 6]},
                "ir_filter": {"modes": ["auto", "day", "night"]},
                "presets": ["daylight", "night_vision", "auto", "custom"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting camera capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Camera capabilities error: {str(e)}")

@camera_router.get("/live")
async def camera_live():
    """Get current camera frame as JPEG"""
    try:
        camera_mgr = get_camera_manager()
        
        # Start streaming if not already
        if not camera_mgr.is_streaming:
            camera_mgr.start_streaming()
            await asyncio.sleep(0.2)  # Reduced wait time
        
        # Add timeout for frame capture
        jpeg_data = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, camera_mgr.get_current_frame),
            timeout=3.0
        )
        
        if jpeg_data is None:
            raise HTTPException(status_code=503, detail="No camera frame available")
        
        return StreamingResponse(
            iter([jpeg_data]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except asyncio.TimeoutError:
        logger.error("Camera live frame timeout")
        raise HTTPException(status_code=503, detail="Camera frame timeout")
    except Exception as e:
        logger.error(f"Error getting camera live frame: {e}")
        raise HTTPException(status_code=500, detail=f"Camera live error: {str(e)}")

@camera_router.get("/live/{resolution}")
async def camera_live_resolution(
    resolution: str = Path(..., description="Resolution: 720p, 1080p, 480p, 240p")
):
    """Get camera frame at specific resolution"""
    try:
        camera_mgr = get_camera_manager()
        
        # Parse resolution
        resolution_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "480p": (640, 480),
            "240p": (320, 240)
        }
        
        if resolution not in resolution_map:
            raise HTTPException(status_code=400, detail=f"Unsupported resolution: {resolution}")
        
        target_res = resolution_map[resolution]
        
        # Set resolution temporarily
        camera_mgr.set_resolution(target_res, is_streaming=True)
        await asyncio.sleep(0.2)  # Wait for resolution change
        
        jpeg_data = camera_mgr.get_current_frame()
        if jpeg_data is None:
            raise HTTPException(status_code=503, detail="No camera frame available")
        
        return StreamingResponse(
            iter([jpeg_data]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        logger.error(f"Error getting camera live frame at {resolution}: {e}")
        raise HTTPException(status_code=500, detail=f"Camera live error: {str(e)}")

@camera_router.get("/stream")
async def camera_stream():
    """Get camera MJPEG stream"""
    try:
        camera_mgr = get_camera_manager()
        
        # Start streaming if not already
        if not camera_mgr.is_streaming:
            camera_mgr.start_streaming()
            await asyncio.sleep(0.5)  # Wait for first frame
        
        async def generate_frames():
            while True:
                try:
                    jpeg_data = camera_mgr.get_current_frame()
                    if jpeg_data is None:
                        # Send a placeholder frame or wait
                        await asyncio.sleep(0.1)
                        continue
                    
                    # MJPEG format: frame boundary + JPEG data
                    frame_data = (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: " + str(len(jpeg_data)).encode() + b"\r\n\r\n" +
                        jpeg_data + b"\r\n"
                    )
                    
                    yield frame_data
                    
                    # Control frame rate
                    await asyncio.sleep(1.0 / camera_mgr.settings.fps)
                    
                except Exception as e:
                    logger.error(f"Error in camera stream: {e}")
                    await asyncio.sleep(1.0)  # Wait before retry
        
        return StreamingResponse(
            generate_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        logger.error(f"Error setting up camera stream: {e}")
        raise HTTPException(status_code=500, detail=f"Camera stream error: {str(e)}")

@camera_router.get("/snapshot")
async def camera_snapshot():
    """Get high-quality camera snapshot"""
    try:
        camera_mgr = get_camera_manager()
        
        # Use FFmpeg for maximum quality with timeout
        jpeg_data = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, camera_mgr.capture_ffmpeg_snapshot),
            timeout=5.0
        )
        
        if jpeg_data is None:
            # Fallback to OpenCV with timeout
            jpeg_data = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, camera_mgr.capture_snapshot),
                timeout=3.0
            )
        
        if jpeg_data is None:
            raise HTTPException(status_code=503, detail="Failed to capture camera snapshot")
        
        return StreamingResponse(
            iter([jpeg_data]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Content-Disposition": "attachment; filename=turtle_snapshot.jpg"
            }
        )
    except asyncio.TimeoutError:
        logger.error("Camera snapshot timeout")
        raise HTTPException(status_code=503, detail="Camera snapshot timeout")
    except Exception as e:
        logger.error(f"Error getting camera snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Camera snapshot error: {str(e)}")

@camera_router.get("/snapshot/{resolution}")
async def camera_snapshot_resolution(
    resolution: str = Path(..., description="Resolution: 720p, 1080p, 480p, 240p")
):
    """Get camera snapshot at specific resolution"""
    try:
        camera_mgr = get_camera_manager()
        
        # Parse resolution
        resolution_map = {
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "480p": (640, 480),
            "240p": (320, 240)
        }
        
        if resolution not in resolution_map:
            raise HTTPException(status_code=400, detail=f"Unsupported resolution: {resolution}")
        
        target_res = resolution_map[resolution]
        
        # Capture snapshot at specified resolution
        jpeg_data = camera_mgr.capture_ffmpeg_snapshot(target_res)
        if jpeg_data is None:
            # Fallback to OpenCV
            jpeg_data = camera_mgr.capture_snapshot(target_res)
        
        if jpeg_data is None:
            raise HTTPException(status_code=503, detail="Failed to capture camera snapshot")
        
        return StreamingResponse(
            iter([jpeg_data]),
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Content-Disposition": f"attachment; filename=turtle_snapshot_{resolution}.jpg"
            }
        )
    except Exception as e:
        logger.error(f"Error getting camera snapshot at {resolution}: {e}")
        raise HTTPException(status_code=500, detail=f"Camera snapshot error: {str(e)}")

@camera_router.get("/settings")
async def get_camera_settings():
    """Get current camera settings"""
    try:
        camera_mgr = get_camera_manager()
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "settings": status.get("settings", {}),
            "resolution": status.get("resolution", {})
        }
    except Exception as e:
        logger.error(f"Error getting camera settings: {e}")
        raise HTTPException(status_code=500, detail=f"Camera settings error: {str(e)}")

@camera_router.post("/settings")
async def update_camera_settings(settings: CameraSettingsRequest):
    """Update camera settings"""
    try:
        camera_mgr = get_camera_manager()
        
        # Update settings
        if settings.exposure_mode is not None:
            camera_mgr.set_exposure(settings.exposure_mode, settings.exposure_time)
        
        if settings.gain is not None:
            camera_mgr.set_gain(settings.gain)
        
        if settings.white_balance_auto is not None:
            camera_mgr.set_white_balance(settings.white_balance_auto, settings.white_balance_temperature)
        
        if any([settings.brightness, settings.contrast, settings.saturation, settings.sharpness]):
            camera_mgr.set_image_quality(
                brightness=settings.brightness,
                contrast=settings.contrast,
                saturation=settings.saturation,
                sharpness=settings.sharpness
            )
        
        # Get updated status
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "message": "Camera settings updated",
            "settings": status.get("settings", {})
        }
    except Exception as e:
        logger.error(f"Error updating camera settings: {e}")
        raise HTTPException(status_code=500, detail=f"Camera settings error: {str(e)}")

@camera_router.post("/resolution")
async def set_camera_resolution(resolution: ResolutionRequest):
    """Set camera resolution"""
    try:
        camera_mgr = get_camera_manager()
        
        # Validate resolution
        valid_resolutions = [(1920, 1080), (1280, 720), (640, 480), (320, 240)]
        if (resolution.width, resolution.height) not in valid_resolutions:
            raise HTTPException(status_code=400, detail="Invalid resolution")
        
        camera_mgr.set_resolution((resolution.width, resolution.height), resolution.is_streaming)
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "message": f"Resolution set to {resolution.width}x{resolution.height}",
            "resolution": {"width": resolution.width, "height": resolution.height}
        }
    except Exception as e:
        logger.error(f"Error setting camera resolution: {e}")
        raise HTTPException(status_code=500, detail=f"Camera resolution error: {str(e)}")

@camera_router.post("/ir-filter")
async def set_ir_filter(request: IRFilterRequest):
    """Set IR filter mode"""
    try:
        camera_mgr = get_camera_manager()
        
        # Parse mode
        mode_map = {
            "auto": IRFilterMode.AUTO,
            "day": IRFilterMode.DAY,
            "night": IRFilterMode.NIGHT
        }
        
        if request.mode not in mode_map:
            raise HTTPException(status_code=400, detail=f"Invalid IR filter mode: {request.mode}")
        
        camera_mgr.set_ir_filter(mode_map[request.mode])
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "message": f"IR filter set to {request.mode} mode"
        }
    except Exception as e:
        logger.error(f"Error setting IR filter: {e}")
        raise HTTPException(status_code=500, detail=f"IR filter error: {str(e)}")

@camera_router.post("/preset")
async def apply_camera_preset(request: PresetRequest):
    """Apply camera preset configuration"""
    try:
        camera_mgr = get_camera_manager()
        
        # Parse preset
        preset_map = {
            "daylight": CameraPreset.DAYLIGHT,
            "night_vision": CameraPreset.NIGHT_VISION,
            "auto": CameraPreset.AUTO,
            "custom": CameraPreset.CUSTOM
        }
        
        if request.preset not in preset_map:
            raise HTTPException(status_code=400, detail=f"Invalid preset: {request.preset}")
        
        camera_mgr.apply_preset(preset_map[request.preset])
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": True,
            "message": f"Camera preset applied: {request.preset}"
        }
    except Exception as e:
        logger.error(f"Error applying camera preset: {e}")
        raise HTTPException(status_code=500, detail=f"Camera preset error: {str(e)}")

@camera_router.get("/restart")
async def restart_camera():
    """Restart camera connection"""
    try:
        camera_mgr = get_camera_manager()
        
        success = camera_mgr.restart()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "success": success,
            "message": "Camera restart successful" if success else "Camera restart failed"
        }
    except Exception as e:
        logger.error(f"Error restarting camera: {e}")
        raise HTTPException(status_code=500, detail=f"Camera restart error: {str(e)}")

@camera_router.get("/stats")
async def camera_stats():
    """Get camera performance statistics"""
    try:
        camera_mgr = get_camera_manager()
        status = camera_mgr.get_status()
        
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "performance": {
                "fps": status.get("fps", 0),
                "connected": status.get("connected", False),
                "streaming": status.get("streaming", False),
                "device": status.get("device", ""),
                "resolution": status.get("resolution", {})
            },
            "settings": status.get("settings", {})
        }
    except Exception as e:
        logger.error(f"Error getting camera stats: {e}")
        raise HTTPException(status_code=500, detail=f"Camera stats error: {str(e)}")

# Initialize camera manager
def init_camera_manager():
    """Initialize the camera manager"""
    global camera_manager
    try:
        # Simple initialization without threading to prevent hanging
        camera_manager = TurtleCameraManager()
        logger.info("✅ Camera manager initialized")
        return camera_manager
    except Exception as e:
        logger.error(f"❌ Failed to initialize camera manager: {e}")
        camera_manager = None
        # Don't raise exception, just log and continue
        return None

def stop_camera_manager():
    """Stop the camera manager"""
    global camera_manager
    if camera_manager:
        camera_manager.stop()
        camera_manager = None
        logger.info("🛑 Camera manager stopped") 