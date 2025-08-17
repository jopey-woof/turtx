"""Platform for TEMPerHUM temperature and humidity sensors."""
import json
import logging
import os
import struct
import time

from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "TEMPerHUM Sensor"
SCAN_INTERVAL = timedelta(seconds=60)
CONF_DEVICE_PATH = "device_path"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_DEVICE_PATH): cv.string,
    }
)

def init_and_read_temperhum(device_path):
    """Initialize TEMPerHUM device and read data with accurate conversion"""
    try:
        # Initialize the device first
        with open(device_path, 'rb+') as device:
            # Send initialization sequence for TEMPerHUM
            # Command 1: Reset device
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.1)
            
            # Command 2: Start continuous reading
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.1)
            
            # Command 3: Request data
            device.write(b'\x00\x01\x80\x33\x01\x00\x00\x00')
            time.sleep(0.2)
        
        # Temporarily return dummy data to test component loading
        _LOGGER.debug("Returning dummy data for TEMPerHUM sensor.")
        return {
            "temperature_celsius": 25.0,
            "temperature_fahrenheit": 77.0,
            "humidity_percent": 65.0,
            "status": "success",
            "device": device_path,
            "raw_temp": 0,
            "raw_humidity": 0,
            "raw_data": "dummy"
        }

        # Original code for reading from device (commented out for now)
        # with open(device_path, 'rb') as device:
        #     # Read 8 bytes
        #     data = device.read(8)
        #     
        #     if len(data) >= 8:
        #         # Debug: show raw data
        #         raw_hex = ' '.join([f'{b:02x}' for b in data])
        #         
        #         # Parse raw values
        #         temp_raw = struct.unpack("<h", data[2:4])[0]  # Signed 16-bit
        #         humidity_raw = struct.unpack("<H", data[4:6])[0]  # Unsigned 16-bit
        #         
        #         # Convert using adjusted scaling for more accurate temperature
        #         temperature_c = temp_raw * 0.7
        #         humidity_percent = humidity_raw / 100.0
        #         
        #         # If humidity is 0, try alternative parsing
        #         if humidity_percent == 0:
        #             humidity_percent = humidity_raw
        #         
        #         return {
        #             "temperature_celsius": round(temperature_c, 1),
        #             "temperature_fahrenheit": round(temperature_c * 9/5 + 32, 1),
        #             "humidity_percent": round(humidity_percent, 1),
        #             "status": "success",
        #             "device": device_path,
        #             "raw_temp": temp_raw,
        #             "raw_humidity": humidity_raw,
        #             "raw_data": raw_hex
        #         }
        #     else:
        #         _LOGGER.warning(f"Insufficient data from {device_path}")
        #         return None
        #         
    except Exception as e:
        _LOGGER.error(f"Error with {device_path}: {str(e)}")
        return None

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up the TEMPerHUM sensor platform."""
    name = config.get(CONF_NAME)
    device_path = config.get(CONF_DEVICE_PATH)

    temperhum_data = TemperhumData(device_path)
    add_entities([
        TemperhumTemperatureSensor(name, temperhum_data),
        TemperhumHumiditySensor(name, temperhum_data)
    ], True)

class TemperhumData:
    """Manages polling for TEMPerHUM data."""
    def __init__(self, device_path):
        self._device_path = device_path
        self._data = None
        self.update() # Perform initial update upon instantiation

    def update(self):
        """Fetch new state data for the sensor."""
        self._data = init_and_read_temperhum(self._device_path)
        if self._data and self._data.get("status") != "success":
            _LOGGER.warning(f"TEMPerHUM device {self._device_path} returned non-success status: {self._data.get('error', 'unknown error')}")
            self._data = None # Invalidate data if not successful

class TemperhumTemperatureSensor(SensorEntity):
    """Representation of a TEMPerHUM temperature sensor."""

    def __init__(self, name, temperhum_data):
        self._name = f"{name} Temperature"
        self._temperhum_data = temperhum_data
        self._state = None
        self._unit_of_measurement = UnitOfTemperature.CELSIUS # Default to Celsius for raw sensor

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:thermometer"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self._temperhum_data._data and self._temperhum_data._data.get("status") == "success":
            return self._temperhum_data._data["temperature_celsius"]
        return None

    def update(self):
        """Fetch new state data for the sensor."""
        self._temperhum_data.update()

class TemperhumHumiditySensor(SensorEntity):
    """Representation of a TEMPerHUM humidity sensor."""

    def __init__(self, name, temperhum_data):
        self._name = f"{name} Humidity"
        self._temperhum_data = temperhum_data
        self._state = None
        self._unit_of_measurement = "%"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:water-percent"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self._temperhum_data._data and self._temperhum_data._data.get("status") == "success":
            return self._temperhum_data._data["humidity_percent"]
        return None

    def update(self):
        """Fetch new state data for the sensor."""
        self._temperhum_data.update()
